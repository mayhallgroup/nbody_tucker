import numpy as np
import scipy
import scipy.linalg
import scipy.io
import copy as cp
import argparse
import scipy.sparse
import scipy.sparse.linalg

from hdvv import *

class Lattice_Block:
    def __init__(self):
        self.index      = 0             # Lattice_Block index
        self.n_sites    = 0             # n_sites
        self.sites      = []            # sites in this Lattice_Block
        self.j12        = np.array([])  # exchange constant matrix
        self.full_dim   = 1             # number of spin configurations on current block 
        
        self.Spi = {}                   # matrix_rep of i'th S^+ in local config basis
        self.Smi = {}                   # matrix_rep of i'th S^- in local config basis
        self.Szi = {}                   # matrix_rep of i'th S^z in local config basis
        
    
    def init(self, _index, _sites, _j12):
        """
        _index  = index of block
        _sites  = list of lattice sites contained in block
        _j12    = full system J12 matrix
        """
        self.index = _index
        self.sites = _sites
        self.n_sites = len(self.sites)
        for si in range(0,self.n_sites):
            self.full_dim *= 2
        if self.n_sites > 0:
            self.j12 = _j12[:,self.sites][self.sites]
    
    def __str__(self):
        out = " Lattice_Block %-4i:" %(self.index)
        for si in range(0,self.n_sites):
            if si < self.n_sites-1:
                out += "%5i," %(self.sites[si])
            else:
                out += "%5i" %(self.sites[si])
        return out
    
    def form_site_operators(self):
        """
            Form the spin operators in the basis of local block states.
        """
        sx = .5*np.array([[0,1.],[1.,0]])
        sy = .5*np.array([[0,(0-1j)],[(0+1j),0]])
        sz = .5*np.array([[1,0],[0,-1]])
        s2 = .75*np.array([[1,0],[0,1]])
        s1 = sx + sy + sz
        I1 = np.eye(2)
 
        sp = sx + sy*(0+1j)
        sm = sx - sy*(0+1j)
 
        sp = sp.real
        sm = sm.real
        for i,s in enumerate(self.sites):
            i1 = np.eye(np.power(2,i))
            i2 = np.eye(np.power(2,self.n_sites-i-1))
            self.Spi[s] = np.kron(i1,np.kron(sp,i2))
            self.Smi[s] = np.kron(i1,np.kron(sm,i2))
            self.Szi[s] = np.kron(i1,np.kron(sz,i2))

    def form_H(self):
        lattice = [1]*self.n_sites
        self.H, tmp, self.S2, self.Sz = form_hdvv_H(lattice, self.j12)  # rewrite this



class Block_Basis:
    def __init__(self,lb,label):
        """
        This is a set of cluster states for a give Lattice_Block

        A Block_Basis object is essentially just a vector subspace of the 
        full Hilbert space associated with Lattice_Block lb. There can be 
        many Block_Basis objects assocated with a single Lattice_Block. 
        
        A Block_Basis object can simply be the P or Q or R space of a 
        Lattice_Block, or it could be (NYI) a quantum number (M_s) subblock 
        of P or Q or S.
        """
        self.lb = cp.deepcopy(lb)   # Lattice_Block object

        self.ms = None  # quantum number of this block. None means don't conserve 
        self.label = cp.deepcopy(label)
        self.vecs = np.array([])
        self.n_vecs = 0
        

    def __str__(self):
        out = ""
        if self.ms != None:
            out = " Block_Basis:  LB=%-4i  Ms=%-4i "%(self.lb.index,self.ms)
        else:
            out = " Block_Basis:  LB=%-4i "%(self.lb.index)
        out += " Dim=%-8i"%self.n_vecs 
        out += str(self.label)
        return out

    def set_vecs(self,v):
        self.vecs = cp.deepcopy(v)
        self.n_vecs = self.vecs.shape[1]

    def append(self,other):
        if self.lb.index != other.lb.index:
            print(" Can't add Block_Basis objects from different Lattice_Blocks")
            exit(-1)
        self.label = self.label + "|" + other.label

        self.vecs = np.hstack((self.vecs,other.vecs))
        self.n_vecs = self.vecs.shape[1]

    def clear(self):
        self.vecs = np.zeros((self.vecs.shape[0],0))
        self.n_vecs = 0
        
    def orthogonalize(self):
        if self.n_vecs == 0:
            return
        self.vecs = scipy.linalg.orth(self.vecs)
        self.n_vecs = self.vecs.shape[1]
        return
#        thresh = 1e-12
#        
#        print self.vecs.T.dot(self.vecs)
#      
#        a = self.vecs * 1 
#        if len(self.vecs.shape) > 1:
#            if self.vecs.shape[1] > 0:
#
#                o = self.vecs.T.dot(self.vecs)
#                #l, v = np.linalg.eigh(o)
#                v,l,V = np.linalg.svd(o)
#        
#                sort_ind = abs(l).argsort()[::-1]
#                l = l[sort_ind]
#                v = v[:,sort_ind]
#                
#                #keep = 0
#                keep = []
#                for li in range(l.shape[0]):
#                    if abs(l[li]) > thresh:
#                        print " %12.8e Keep"%l[li]
#                        #keep += 1
#                        keep.append(li)
#                    else:
#                        print " %12.8e Toss"%l[li]
#                
#                a = self.vecs.dot(v[keep,:].T)
#               
#        else:
#            self.vecs.shape = (self.vecs.shape[0],1)
#        
#        self.n_vecs = self.vecs.shape[1]
#        #print self.vecs
#        self.vecs = a*1
#        print "here1:"
#        print a.T.dot(a)
#        print self.vecs.T.dot(self.vecs)
#        print "here2:"




class Tucker_Block:
    """
    Essentially a collection of Block_Basis objects, which defines a particular subspace of the full systems subspace
        which is given as the direct product space of each Block_Basis.
    """
    def __init__(self):
        #self.id = cp.deepcopy(_id)  # (-1):PPP, (1):PQP, (1,3):QPQ, etc 
        self.start = 0              # starting point in super ci 
        self.stop = 0               # stopping point in super ci
        self.address = []           # list of block spaces. e.g.: [0,0,0,1,0,0,1,1,0] means that Blocks 3,6,7 are in their
                                    #       Q-spaces. This doesn't specify which subspace of their Q-space, just that the local
                                    #       states in 3,6,7 are orthogonal to their P spaces
        self.blocks = []            # list of references to Block_Basis objects
        
        self.n_blocks = 0
        self.full_dim = 1
        self.block_dims = [] 
        self.label = "" 
   

    def add_block(self,_block):
        self.blocks.append(_block)
        self.full_dim = self.full_dim * _block.n_vecs
        self.stop = self.start + self.full_dim
        self.address.append(_block.label)
        self.n_blocks = len(self.blocks)
        self.block_dims.append(_block.n_vecs)

    def set_block(self,_block):
        bi = _block.lb.index   # cluster id
        self.blocks[bi] = _block
        self.full_dim = 1
        for bj in self.blocks:
            self.full_dim = self.full_dim * bj.n_vecs
        self.address[bi] = (_block.label)
        self.stop = self.start + self.full_dim
        
        self.block_dims[bi] = _block.n_vecs

    def set_start(self,start):
        self.start = cp.deepcopy(start)
        self.stop = self.start + self.full_dim

    def refresh_dims(self):
        self.full_dim = 1
        for bj in range(self.n_blocks):
            Bj = self.blocks[bj] 
            assert(Bj.vecs.shape[1] == Bj.n_vecs)
            self.full_dim = self.full_dim * Bj.n_vecs
            self.address[bj] = (Bj.label)
            self.block_dims[bj] = Bj.n_vecs
        
        self.stop = self.start + self.full_dim

    def update_label(self):
        """
        Use this to get the correct label after changing a bock basis object
        """
        active = []
        n_active = 0
        for bi in range(self.n_blocks):
            if self.blocks[bi].label[0] == "Q":
                n_active += 1
                active.append(bi)
        active.insert(0, n_active)
        self.label = tuple(active)

    def build_H(j12):
        """
        Build Hamiltonian in Tucker Block
        """

    def __str__(self):
        out = "" 
        for b in self.blocks:
            out += "%4i"%b.n_vecs
        out += " :: "+ "%-6i"%self.full_dim
        for a in self.address:
            if a[0] == "P":
                continue
            out += "%-10s "%str(a)
        return out


#######################################################################################



def build_H(tb_l, tb_r,j12):
  # {{{
    """
    Build the Hamiltonian between two tucker blocks, tb_l and tb_r, without ever constructing a full hilbert space
    """

    assert(len(tb_l.blocks) == len(tb_r.blocks))
    n_blocks = len(tb_l.blocks)
   
    # Make sure both left and right contain the same lattice_blocks
    for bi in range(n_blocks):
        assert(tb_l.blocks[bi].lb.index == tb_r.blocks[bi].lb.index)

    
    H_dim_layout = []  # dimensions of Ham block as a tensor (d1,d2,..,d1',d2',...)
    H_dim_layout = np.append(tb_l.block_dims,tb_r.block_dims)
   
    """
    form one-block and two-block terms of H separately
        1-body

            for each block, form Hamiltonian in subspace, and combine
            with identity on other blocks

        2-body
            
            for each block-dimer, form Hamiltonian in subspace, and combine
            with identity on other blocks
    """
   
    """
    <RPRP|H|PQQP>
        diff 1,2,3
        <R|H|P><P|Q><R|Q><P|P> = 0
        <R|P><P|H|Q><R|Q><P|P> = 0
        <R|P><P|Q><R|H|Q><P|P> = 0
        <R|P><P|Q><R|Q><P|H|P> = 0
        
        <RP|H12|PQ><R|Q><P|P>  != 0

    <QPQP|H|PQQP>
        diff 1,2
        <RP|H12|PQ><R|Q><P|P>  != 0

    <QPPP|H|RRPP>
        diff 1
        <Q|H|R><PPP|RPP>         = 0
        <Q|R><P|H|R><PP|PP>     != 0
        <QP|H12|RR><PP|PP>      != 0
        <Q|R><PP|H12|RP><P|P>   != 0
    """
    
    # How many blocks are different between left and right?
    different = []  # list of lattice blocks indices that have different vector spaces between tb_l and tb_r
    for bi in range(0,n_blocks):
        if tb_l.blocks[bi].label[0] != tb_r.blocks[bi].label[0]:
            different.append(bi)
            assert(tb_l.blocks[bi].lb.index ==  tb_r.blocks[bi].lb.index ) 
        
    
    #print(" in Build_H")
    #print tb_l.label,tb_r.label
    #print "different", different
   
    
    H  = np.zeros((tb_l.full_dim,tb_r.full_dim))
    S2 = np.zeros((tb_l.full_dim,tb_r.full_dim))
   
    #print " Ham block size", H.shape, H_dim_layout
    H.shape = H_dim_layout
    S2.shape = H_dim_layout
    #   Add up all the one-body contributions, making sure that the results is properly dimensioned for the 
    #   target subspace

    if len(different) == 0:

        assert(tb_l.full_dim == tb_r.full_dim)
        
        full_dim = tb_l.full_dim
        
        #<abcd|H1+H2+H3+H4|abcd>
        #
        #   <a|H1|a> Ib Ic Id
        # + Ia <b|H1|b> Ic Id + etc

        for bi in range(0,n_blocks):
            Bi = tb_l.blocks[bi]
            dim_e = full_dim / tb_l.block_dims[bi] 
          
            lbi = Bi.lb

            h1 = tb_l.blocks[bi].vecs.T.dot( lbi.H).dot(tb_r.blocks[bi].vecs)
            s1 = tb_l.blocks[bi].vecs.T.dot( lbi.S2).dot(tb_r.blocks[bi].vecs)
            #h = np.kron(h1,np.eye(dim_e))   
            #print tb_l,tb_r
            #print tb_l.blocks[bi],tb_r.blocks[bi]
            #print tb_l.block_dims[bi], tb_r.block_dims[bi], tb_l.block_dims, tb_r.block_dims
            #print h1.shape, lbi.H.shape
            #print tb_l.blocks[bi].vecs.shape, tb_r.blocks[bi].vecs.shape
            h1.shape = (tb_l.block_dims[bi],tb_r.block_dims[bi])
            s1.shape = (tb_l.block_dims[bi],tb_r.block_dims[bi])
        
            tens_inds    = []
            tens_inds.extend([bi])
            tens_inds.extend([bi+n_blocks])
            for bj in range(0,n_blocks):
                if (bi != bj):
                    tens_inds.extend([bj])
                    tens_inds.extend([bj+n_blocks])
                    assert(tb_l.block_dims[bj] == tb_r.block_dims[bj] )
                    h1 = np.tensordot(h1,np.eye(tb_l.block_dims[bj]),axes=0)
                    s1 = np.tensordot(s1,np.eye(tb_l.block_dims[bj]),axes=0)

            sort_ind = np.argsort(tens_inds)

            H  += h1.transpose(sort_ind)
            S2 += s1.transpose(sort_ind)
        
        
        #   <ab|H12|ab> Ic Id
        # + <ac|H13|ac> Ib Id
        # + Ia <bc|H23|bc> Id + etc
        
        for bi in range(0,n_blocks):
            for bj in range(bi+1,n_blocks):
                Bi = tb_l.blocks[bi]
                Bj = tb_l.blocks[bj]
            
                lbi = Bi.lb
                lbj = Bj.lb
                
                dim_e = full_dim / tb_l.block_dims[bi] / tb_l.block_dims[bj]

                #build full Hamiltonian on sublattice
                h2,s2 = build_dimer_H(tb_l, tb_r, bi, bj, j12)
                
                h2.shape = (tb_l.block_dims[bi],tb_l.block_dims[bj],tb_r.block_dims[bi],tb_r.block_dims[bj])
                s2.shape = (tb_l.block_dims[bi],tb_l.block_dims[bj],tb_r.block_dims[bi],tb_r.block_dims[bj])

                #h = np.kron(h12,np.eye(dim_e))   
            
                tens_inds    = []
                tens_inds.extend([bi,bj])
                tens_inds.extend([bi+n_blocks, bj+n_blocks])
                for bk in range(0,n_blocks):
                    if (bk != bi) and (bk != bj):
                        tens_inds.extend([bk])
                        tens_inds.extend([bk+n_blocks])
                        assert(tb_l.block_dims[bk] == tb_r.block_dims[bk] )
                        h2 = np.tensordot(h2,np.eye(tb_l.block_dims[bk]),axes=0)
                        s2 = np.tensordot(s2,np.eye(tb_l.block_dims[bk]),axes=0)
               
                sort_ind = np.argsort(tens_inds)
               
                H  += h2.transpose(sort_ind)
                S2 += s2.transpose(sort_ind)
    
    
    
    
    
    
    elif len(different) == 1:
       
        
        full_dim_l = tb_l.full_dim
        full_dim_r = tb_r.full_dim
        
        #<abcd|H1+H2+H3+H4|abcd>
        #
        #   <a|H1|a> Ib Ic Id  , for block 1 being different


        bi = different[0] 

        lbi = tb_l.blocks[bi].lb     # Bi is the Lattice_Block which is different

        h1 = tb_l.blocks[bi].vecs.T.dot( lbi.H).dot(tb_r.blocks[bi].vecs)
        s1 = tb_l.blocks[bi].vecs.T.dot( lbi.S2).dot(tb_r.blocks[bi].vecs)
        
        h1.shape = (tb_l.block_dims[bi],tb_r.block_dims[bi])
        s1.shape = (tb_l.block_dims[bi],tb_r.block_dims[bi])

        
        tens_inds    = []
        tens_inds.extend([bi])
        tens_inds.extend([bi+n_blocks])
        for bj in range(0,n_blocks):
            if (bi != bj):
                tens_inds.extend([bj])
                tens_inds.extend([bj+n_blocks])
                
                Oj = np.eye(tb_l.block_dims[bj])
                if tb_l.blocks[bj].label[0] == "Q" or tb_r.blocks[bj].label[0] == "Q" :
                    Oj = tb_l.blocks[bj].vecs.T.dot(tb_r.blocks[bj].vecs)
                
                h1 = np.tensordot(h1,Oj,axes=0)
                s1 = np.tensordot(s1,Oj,axes=0)

        sort_ind = np.argsort(tens_inds)

        H  += h1.transpose(sort_ind)
        S2 += s1.transpose(sort_ind)
        
        
        #   <ab|H12|Ab> Ic Id
        # + <ac|H13|Ac> Ib Id
        # + <ad|H13|Ad> Ib Id
        
        for bj in range(0,bi):
            lbj = tb_l.blocks[bj].lb

            assert(lbj.index == tb_r.blocks[bj].lb.index)

            
            #build full Hamiltonian on sublattice
            h2,s2 = build_dimer_H(tb_l, tb_r, bj, bi, j12)
          
            h2.shape = (tb_l.block_dims[bj],tb_l.block_dims[bi],tb_r.block_dims[bj],tb_r.block_dims[bi])
            s2.shape = (tb_l.block_dims[bj],tb_l.block_dims[bi],tb_r.block_dims[bj],tb_r.block_dims[bi])
         
            
            #h = np.kron(h12,np.eye(dim_e))   
            
            tens_dims    = []
            tens_inds    = []
            tens_inds.extend([bj,bi])
            tens_inds.extend([bj+n_blocks, bi+n_blocks])
            for bk in range(0,n_blocks):
                if (bk != bi) and (bk != bj):
                    tens_inds.extend([bk])
                    tens_inds.extend([bk+n_blocks])
        
                    Ok = np.eye(tb_l.block_dims[bk])
                    if tb_l.blocks[bk].label[0] == "Q" or tb_r.blocks[bk].label[0] == "Q" :
                        #print tb_l.label, tb_r.label
                        #print tb_l.blocks[bk].label, tb_r.blocks[bk].label
                        Ok = tb_l.blocks[bk].vecs.T.dot(tb_r.blocks[bk].vecs)
                    h2 = np.tensordot(h2,Ok,axes=0)
                    s2 = np.tensordot(s2,Ok,axes=0)
            
            sort_ind = np.argsort(tens_inds)
            H  += h2.transpose(sort_ind)
            S2 += s2.transpose(sort_ind)
        
        for bj in range(bi+1, n_blocks):
            lbj = tb_l.blocks[bj].lb

            assert(lbj.index == tb_r.blocks[bj].lb.index)
            
            
            #build full Hamiltonian on sublattice
            h2,s2 = build_dimer_H(tb_l, tb_r, bi, bj, j12)
          
            h2.shape = (tb_l.block_dims[bi],tb_l.block_dims[bj],tb_r.block_dims[bi],tb_r.block_dims[bj])
            s2.shape = (tb_l.block_dims[bi],tb_l.block_dims[bj],tb_r.block_dims[bi],tb_r.block_dims[bj])
         
            
            #h = np.kron(h12,np.eye(dim_e))   
            
            tens_dims    = []
            tens_inds    = []
            tens_inds.extend([bi,bj])
            tens_inds.extend([bi+n_blocks, bj+n_blocks])
            for bk in range(0,n_blocks):
                if (bk != bi) and (bk != bj):
                    tens_inds.extend([bk])
                    tens_inds.extend([bk+n_blocks])
                    
                    Ok = np.eye(tb_l.block_dims[bk])
                    if tb_l.blocks[bk].label[0] == "Q" or tb_r.blocks[bk].label[0] == "Q" :
                        Ok = tb_l.blocks[bk].vecs.T.dot(tb_r.blocks[bk].vecs)
                
                    h2 = np.tensordot(h2,Ok,axes=0)
                    s2 = np.tensordot(s2,Ok,axes=0)
            
            sort_ind = np.argsort(tens_inds)
            H  += h2.transpose(sort_ind)
            S2 += s2.transpose(sort_ind)
    
    
    
    
    elif len(different) == 2:
    
        full_dim_l = tb_l.full_dim
        full_dim_r = tb_r.full_dim
        #<abcd|H1+H2+H3+H4|abcd> = 0


        bi = different[0] 
        bj = different[1] 

        lbi = tb_l.blocks[bi].lb
        lbj = tb_l.blocks[bj].lb

        assert(lbi.index == tb_r.blocks[bi].lb.index)
        assert(lbj.index == tb_r.blocks[bj].lb.index)

        #dim_e_l = full_dim_l / tb_l.block_dims[bi] / tb_l.block_dims[bj] 
        #dim_e_r = full_dim_r / tb_r.block_dims[bi] / tb_r.block_dims[bj] 

        #assert(dim_e_l == dim_e_r)
        #dim_e = dim_e_l
        
        
        #  <ac|H13|Ac> Ib Id  for 1 3 different
        
        #build full Hamiltonian on sublattice
        #h12 = build_dimer_H(tb_l, tb_r, Bi, Bj, j12)
        h2,s2 = build_dimer_H(tb_l, tb_r, bi, bj, j12)
       
        h2.shape = (tb_l.block_dims[bi],tb_l.block_dims[bj],tb_r.block_dims[bi],tb_r.block_dims[bj])
        s2.shape = (tb_l.block_dims[bi],tb_l.block_dims[bj],tb_r.block_dims[bi],tb_r.block_dims[bj])
        #h2 = np.kron(h12,np.eye(dim_e))   
        
        tens_dims    = []
        tens_inds    = []
        tens_inds.extend([bi,bj])
        tens_inds.extend([bi+n_blocks, bj+n_blocks])
        for bk in range(0,n_blocks):
            if (bk != bi) and (bk != bj):
                tens_inds.extend([bk])
                tens_inds.extend([bk+n_blocks])
                tens_dims.extend([tb_l.block_dims[bk]])
                tens_dims.extend([tb_r.block_dims[bk]])
        
                Ok = np.eye(tb_l.block_dims[bk])
                if tb_l.blocks[bk].label[0] == "Q" or tb_r.blocks[bk].label[0] == "Q" :
                    Ok = tb_l.blocks[bk].vecs.T.dot(tb_r.blocks[bk].vecs)
                
                h2 = np.tensordot(h2,Ok,axes=0)
                s2 = np.tensordot(s2,Ok,axes=0)
        
        sort_ind = np.argsort(tens_inds)
        H += h2.transpose(sort_ind)
        S2 += s2.transpose(sort_ind)

    H = H.reshape(tb_l.full_dim,tb_r.full_dim)
    S2 = S2.reshape(tb_l.full_dim,tb_r.full_dim)
    return H,S2
# }}}



def build_overlap(tb_l, tb_r):
  # {{{
    """
    Build the Overlap between two tucker blocks, tb_l and tb_r
    """

    assert(len(tb_l.blocks) == len(tb_r.blocks))
    n_blocks = len(tb_l.blocks)
   
    # Make sure both left and right contain the same lattice_blocks
    for bi in range(n_blocks):
        assert(tb_l.blocks[bi].lb.index == tb_r.blocks[bi].lb.index)

    
    O_dim_layout = []  # dimensions of Ham block as a tensor (d1,d2,..,d1',d2',...)
    O_dim_layout = np.append(tb_l.block_dims,tb_r.block_dims)
   
    """
    """
    
    
    # How many blocks are different between left and right?
    different = []  # list of lattice blocks indices that have different vector spaces between tb_l and tb_r
    for bi in range(0,n_blocks):
        if tb_l.blocks[bi].label != tb_r.blocks[bi].label:
            different.append(bi)
            assert(tb_l.blocks[bi].lb.index ==  tb_r.blocks[bi].lb.index ) 
        
    
   
    
    O  = np.zeros((tb_l.full_dim,tb_r.full_dim))
    O.shape = O_dim_layout
    
    full_dim = tb_l.full_dim

    for bi in range(0,n_blocks):
        Bi = tb_l.blocks[bi]
        dim_e = full_dim / tb_l.block_dims[bi] 
      
        lbi = Bi.lb

        o1 = tb_l.blocks[bi].vecs.T.dot(tb_r.blocks[bi].vecs)
        o1.shape = (tb_l.block_dims[bi],tb_r.block_dims[bi])
    
        tens_inds    = []
        tens_inds.extend([bi])
        tens_inds.extend([bi+n_blocks])
        for bj in range(0,n_blocks):
            if (bi != bj):
                tens_inds.extend([bj])
                tens_inds.extend([bj+n_blocks])
                o1 = np.tensordot(o1,np.eye(tb_l.block_dims[bj]),axes=0)

        sort_ind = np.argsort(tens_inds)

        O  += o1.transpose(sort_ind)
        

    O = O.reshape(tb_l.full_dim,tb_r.full_dim)
    return O
# }}}


def build_dimer_H(tb_l, tb_r, bi, bj,j12):
# {{{
 
    #print(bi,bj)
    #print(tb_l.block_dims)
    #print(tb_r.block_dims)

    dim_l = tb_l.blocks[bi].n_vecs * tb_l.blocks[bj].n_vecs

    #print (bi,bj), tb_l.block_dims, ":", tb_r.block_dims
    h12 = np.zeros((tb_l.block_dims[bi]*tb_l.block_dims[bj],tb_r.block_dims[bi]*tb_r.block_dims[bj]))
    s2 = np.zeros((tb_l.block_dims[bi]*tb_l.block_dims[bj],tb_r.block_dims[bi]*tb_r.block_dims[bj]))
    sz = np.zeros((tb_l.block_dims[bi]*tb_l.block_dims[bj],tb_r.block_dims[bi]*tb_r.block_dims[bj]))

    h12.shape = (tb_l.block_dims[bi], tb_r.block_dims[bi], tb_l.block_dims[bj], tb_r.block_dims[bj])
    s2.shape = (tb_l.block_dims[bi], tb_r.block_dims[bi], tb_l.block_dims[bj], tb_r.block_dims[bj])
    sz.shape = (tb_l.block_dims[bi], tb_r.block_dims[bi], tb_l.block_dims[bj], tb_r.block_dims[bj])
   
    # Get the four distinct vector spaces
    bbli = tb_l.blocks[bi].vecs     # block basis for lattice block i in tucker block l
    bbri = tb_r.blocks[bi].vecs     # block basis for lattice block i in tucker block r
    bblj = tb_l.blocks[bj].vecs     # block basis for lattice block j in tucker block l
    bbrj = tb_r.blocks[bj].vecs     # block basis for lattice block j in tucker block r
   
    # make sure we are talking about the same lattice block in left and right
    assert(tb_l.blocks[bi].lb.index == tb_r.blocks[bi].lb.index)
    assert(tb_l.blocks[bj].lb.index == tb_r.blocks[bj].lb.index)

    lbi = tb_l.blocks[bi].lb    # tb_r could also have been used
    lbj = tb_l.blocks[bj].lb    # tb_r could also have been used

    for si in lbi.sites:
        
        spi = bbli.T.dot(lbi.Spi[si]).dot(bbri)
        smi = bbli.T.dot(lbi.Smi[si]).dot(bbri)
        szi = bbli.T.dot(lbi.Szi[si]).dot(bbri)
       
        #print spi.shape, smi.shape, szi.shape
        #print lbi.Spi[si].shape, lbi.Smi[si].shape, lbi.Szi[si].shape
        #print bbli.shape, bbri.shape 
        for sj in lbj.sites:
            #if abs(j12[si,sj]) < 1e-8:
            #    continue
            spj = bblj.T.dot(lbj.Spi[sj]).dot(bbrj)
            smj = bblj.T.dot(lbj.Smi[sj]).dot(bbrj)
            szj = bblj.T.dot(lbj.Szi[sj]).dot(bbrj)
           
            s1s2  = np.tensordot(spi,smj, axes=0)
            s1s2 += np.tensordot(smi,spj, axes=0)
            s1s2 += 2 * np.tensordot(szi,szj, axes=0)
            
            #print spj.shape, smj.shape, szj.shape

            h12 -= j12[si,sj] * s1s2
            s2  += s1s2

    sort_ind = [0,2,1,3]
    h12 = h12.transpose(sort_ind)
    h12 = h12.reshape(tb_l.block_dims[bi]*tb_l.block_dims[bj],tb_r.block_dims[bi]*tb_r.block_dims[bj])
    s2 = s2.transpose(sort_ind)
    s2 = s2.reshape(tb_l.block_dims[bi]*tb_l.block_dims[bj],tb_r.block_dims[bi]*tb_r.block_dims[bj])
    return h12, s2
# }}}


def build_tucker_blocked_H(tucker_blocks, j12):
    #{{{
    dim_tot = 0
    for ti in sorted(tucker_blocks):
        tbi = tucker_blocks[ti]
        dim_tot += tbi.full_dim


    #O = np.zeros((dim_tot, dim_tot))
    H = np.zeros((dim_tot, dim_tot))
    S2 = np.zeros((dim_tot, dim_tot))

        
    for t_l in sorted(tucker_blocks):
        for t_r in sorted(tucker_blocks):
            tb_l = tucker_blocks[t_l]
            tb_r = tucker_blocks[t_r]
            
            
            if tb_l.full_dim == 0:
                continue       
            if tb_r.full_dim == 0:
                continue
            
            if tb_r.label >= tb_l.label:
                #print t_l, t_r, tb_l, tb_r
                #print 
                h,s2 = build_H(tb_l, tb_r, j12)
                #o = build_overlap(tb_l, tb_r)
                H[tb_l.start:tb_l.stop, tb_r.start:tb_r.stop] = h 
                H[tb_r.start:tb_r.stop, tb_l.start:tb_l.stop] = h.T
                S2[tb_l.start:tb_l.stop, tb_r.start:tb_r.stop] = s2 
                S2[tb_r.start:tb_r.stop, tb_l.start:tb_l.stop] = s2.T

    return H, S2#, O
    #}}}


def tucker_block_overlap(tb_l, tb_r):
    """
    Compute the overlap of tb_l and tb_r
    """
    O  = np.zeros((tb_l.full_dim,tb_r.full_dim))
    overlap = 1
    for bi in range(tb_l.n_blocks):
        v_l = tb_l.blocks[bi].vecs
        v_r = tb_r.blocks[bi].vecs
        overlap *= np.trace(v_l.T.dot(v_r))

    print "%12.8f"%overlap
    return O


def form_pt2_v(tucker_blocks, tucker_blocks_pt, l, v0, j12):
    """# {{{

        E(2) = v_sA H_AX [D_XX - E_s^0]^-1 H_XA v_As

             = v_sA H_AX

        pt_type: mp or en
                
                 mp uses H1 as zeroth-order Hamiltonian
                 en uses the diagonal of H for zeroth-order
    """

    n_roots = v0.shape[1]

    assert(l.shape[0] == n_roots)
    """
    e2 = sum_ab(in A) sum_x(in X)  c_as <a|H|x> d_x <x|H|b> c_bs
    """
    dim_tot_X = 0
    dim_tot_A = 0
    for t_l in sorted(tucker_blocks_pt):
        tb_l = tucker_blocks_pt[t_l]
        dim_tot_X += tb_l.full_dim
    for t_l in sorted(tucker_blocks):
        tb_l = tucker_blocks[t_l]
        dim_tot_A += tb_l.full_dim
    
    e2 = np.zeros((n_roots))
    DHv = np.zeros((dim_tot_X,n_roots))
    
    H_Xs = np.zeros((dim_tot_X, n_roots))
    D_X = np.zeros((dim_tot_X))
    
    do_2b_diag = 0
    for t_l in sorted(tucker_blocks_pt):
        tb_l = tucker_blocks_pt[t_l]
        D_X[tb_l.start:tb_l.stop] = build_H_diag(tb_l, tb_l, j12, do_2b_diag)
        
        #print D_X[tb_l.start:tb_l.stop]
        for t_r in sorted(tucker_blocks):
            tb_r = tucker_blocks[t_r]

            hv,tmp = build_H(tb_l, tb_r, j12)
            #hv,s2v = build_Hv(tb_l, tb_r, j12,v[tb_r.start:tb_r.stop,:])
            H_Xs[tb_l.start:tb_l.stop,:] += hv.dot(v0[tb_r.start:tb_r.stop,:])


    for s in range(0, n_roots):
        dx = 1/(l[s]-D_X)
        DHv[:,s] = np.multiply(dx, H_Xs[:,s])
        e2[s] = H_Xs[:,s].T.dot(DHv[:,s])
# }}}
    return e2,DHv

def build_H_diag(tb_l, tb_r,j12, do_2b_diag):
  # {{{
    """
    Build the Hamiltonian between two tensor blocks, tb_l and tb_r, without ever constructing a full hilbert space

    do_2b_diag: should the 2-block contributions to the diagonal be computed?
    """

    assert(tb_l.n_blocks == tb_r.n_blocks)
    n_blocks = tb_l.n_blocks
   
    
    H_dim_layout = []  # dimensions of Ham block as a tensor (d1,d2,..,d1',d2',...)
    H_dim_layout = tb_l.block_dims
   
    """
    form one-block and two-block terms of H separately
        1-body

            for each block, form Hamiltonian in subspace, and combine
            with identity on other blocks

        2-body
            
            for each block-dimer, form Hamiltonian in subspace, and combine
            with identity on other blocks
    """
    # How many blocks are different between left and right?
    different = []
    
    Hd  = np.zeros((tb_l.full_dim))
   
    #print " Ham block size", H.shape, H_dim_layout
    Hd.shape = H_dim_layout
    #   Add up all the one-body contributions, making sure that the results is properly dimensioned for the 
    #   target subspace

    assert(tb_l.label == tb_r.label)
    full_dim = tb_l.full_dim
    #<abcd|H1+H2+H3+H4|abcd>
    #
    #   <a|H1|a> Ib Ic Id
    # + Ia <b|H1|b> Ic Id + etc

    for bi in range(0,n_blocks):
        Bi = tb_l.blocks[bi]
        dim_e = full_dim / tb_l.block_dims[bi] 
    
        lbi = Bi.lb
        h1 = tb_l.blocks[bi].vecs.T.dot( lbi.H).dot(tb_r.blocks[bi].vecs).diagonal()
        h1.shape = (tb_l.block_dims[bi])
   
        #print h1
        tens_inds    = []
        tens_inds.extend([bi])
        for bj in range(0,n_blocks):
            if (bi != bj):
                tens_inds.extend([bj])
                assert(tb_l.block_dims[bj] == tb_r.block_dims[bj] )
                h1 = np.tensordot(h1,np.eye(tb_l.block_dims[bj]).diagonal(),axes=0)

        sort_ind = np.argsort(tens_inds)
       
        #print Hd.shape, h1.shape

        Hd  += h1.transpose(sort_ind)
    
    
    #   <ab|H12|ab> Ic Id
    # + <ac|H13|ac> Ib Id
    # + Ia <bc|H23|bc> Id + etc
    
    # do 2body diagonal terms?
    if do_2b_diag:
        print "NYI"
        exit(-1)
        for bi in range(0,n_blocks):
            for bj in range(bi+1,n_blocks):
                Bi = blocks[bi]
                Bj = blocks[bj]
                dim_e = full_dim / tb_l.block_dims[bi] / tb_l.block_dims[bj]
        
                #build full Hamiltonian on sublattice
                h2,s2 = build_dimer_H(tb_l, tb_r, Bi, Bj, j12)
                h2 = h2.diagonal()
                h2.shape = (tb_l.block_dims[bi],tb_l.block_dims[bj])
        
                #h = np.kron(h12,np.eye(dim_e))   
            
                tens_inds    = []
                tens_inds.extend([bi,bj])
                for bk in range(0,n_blocks):
                    if (bk != bi) and (bk != bj):
                        tens_inds.extend([bk])
                        assert(tb_l.block_dims[bk] == tb_r.block_dims[bk] )
                        h2 = np.tensordot(h2,np.eye(tb_l.block_dims[bk]).diagonal(),axes=0)
             
                sort_ind = np.argsort(tens_inds)
               
                Hd  += h2.transpose(sort_ind)
    
    
    Hd.shape = (tb_l.full_dim)
    return Hd
# }}}


