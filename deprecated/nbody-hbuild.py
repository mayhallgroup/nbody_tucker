#! /usr/bin/env python
import numpy as np
import scipy
import scipy.linalg
import scipy.io
import copy as cp
import argparse
import scipy.sparse
import scipy.sparse.linalg
#import sys
#sys.path.insert(0, '../')


from hdvv import *

def printm(m):
    # {{{
    """ print matrix """
    for r in m:
        for ri in r:
            print "%10.1e" %ri,
        print
    # }}}

def get_guess_vectors(lattice, j12, blocks, n_p_states, n_q_states):
    # {{{
    print " Generate initial guess vectors"
    p_states = []
    q_states = []
    for bi,b in enumerate(blocks):
        # form block hamiltonian
        j_b = np.zeros([len(b),len(b)])
        j_b = j12[:,b][b]
        lat_b = lattice[b]
        H_b, tmp, S2_b, Sz_b = form_hdvv_H(lat_b,j_b)
    
        # Diagonalize an arbitrary linear combination of the quantum numbers we insist on preserving
        l_b,v_b = np.linalg.eigh(H_b + Sz_b + S2_b) 
        l_b = v_b.transpose().dot(H_b).dot(v_b).diagonal()
        
        sort_ind = np.argsort(l_b)
        l_b = l_b[sort_ind]
        v_b = v_b[:,sort_ind]
            

        print " Guess eigenstates"
        for l in l_b:
            print "%12.8f" %l
        p_states.extend([v_b[:,0:n_p_states[bi]]])
        #q_states.extend([v_b[:,n_p_states[bi]::]])
        q_states.extend([v_b[:,n_p_states[bi]: n_p_states[bi]+n_q_states[bi]]])
    return p_states, q_states
    # }}}

def form_superblock_hamiltonian(lattice, j12, blocks, block_list):
    # {{{
    print " Generate sub-block Hamiltonian"
    super_block = []
    for bi,b in enumerate(block_list):
	# form block hamiltonian
        super_block.extend(blocks[b])
    
    j_b = np.zeros([len(super_block),len(super_block)])
    j_b = j12[:,super_block][super_block]
    lat_b = lattice[super_block]
    H_b, tmp, S2_b, Sz_b = form_hdvv_H(lat_b,j_b)
    return H_b, S2_b, Sz_b
    # }}}

def form_compressed_zero_order_hamiltonian_diag(vecs,Hi):
    # {{{
    dim = 1 # dimension of subspace
    dims = [] # list of mode dimensions (size of hilbert space on each fragment) 
    for vi,v in enumerate(vecs):
        dim = dim*v.shape[1]
        dims.extend([v.shape[1]])
    H = np.zeros((dim,dim))
    n_dims = len(dims)


    H1 = cp.deepcopy(Hi)
    for vi,v in enumerate(vecs):
        H1[vi] = np.dot(v.transpose(),np.dot(Hi[vi],v))

    
    dimsdims = dims
    dimsdims = np.append(dims,dims)

    #Htest = Htest.reshape(dimsdims)
    #   Add up all the one-body contributions, making sure that the results is properly dimensioned for the 
    #   target subspace
    dim_i1=1 #   dimension of space to the left
    dim_i2=dim #   dimension of space to the right
    
    for vi,v in enumerate(vecs):
        i1 = np.eye(dim_i1)
        dim_i2 = dim_i2/v.shape[1]
        i2 = np.eye(dim_i2)
        
        #print "dim_i1  :  dim_i2", dim_i1, dim_i2, dim
        H += np.kron(i1,np.kron(H1[vi],i2))
        
        #nv = v.shape[1]
        #test = np.ones(len(dimsdims)).astype(int)
        #test[vi] = nv
        #test[vi+len(dims)] = nv
        
        #h = cp.deepcopy(H1[vi])
        #h = h.reshape(test)
        #Htest = np.einsum('ijkljk->ijklmn',Htest,h)
        
        dim_i1 = dim_i1 * v.shape[1]

     

    #H = H.reshape(dim,dim)
<<<<<<< HEAD:deprecated/nbody-hbuild.py
    #print "     Size of Hamitonian block: ", H.shape
    return H.diagonal()
    # }}}

def form_compressed_zero_order_hamiltonian_diag1(vecs,Hi):
    # {{{
    dim = 1 # dimension of subspace
    dims = [] # list of mode dimensions (size of hilbert space on each fragment) 
    for vi,v in enumerate(vecs):
        dim = dim*v.shape[1]
        dims.extend([v.shape[1]])
    H = np.zeros((dim,dim))
    n_dims = len(dims)


    H1 = cp.deepcopy(Hi)
    for vi,v in enumerate(vecs):
        H1[vi] = np.dot(v.transpose(),np.dot(Hi[vi],v))

    
    dimsdims = dims
    dimsdims = np.append(dims,dims)

    #Htest = Htest.reshape(dimsdims)
    #   Add up all the one-body contributions, making sure that the results is properly dimensioned for the 
    #   target subspace
    dim_i1=1 #   dimension of space to the left
    dim_i2=dim #   dimension of space to the right
    
    for vi,v in enumerate(vecs):
        i1 = np.eye(dim_i1)
        dim_i2 = dim_i2/v.shape[1]
        i2 = np.eye(dim_i2)
        
        #print "dim_i1  :  dim_i2", dim_i1, dim_i2, dim
        H += np.kron(i1,np.kron(H1[vi],i2))
        
        #nv = v.shape[1]
        #test = np.ones(len(dimsdims)).astype(int)
        #test[vi] = nv
        #test[vi+len(dims)] = nv
        
        #h = cp.deepcopy(H1[vi])
        #h = h.reshape(test)
        #Htest = np.einsum('ijkljk->ijklmn',Htest,h)
        
        dim_i1 = dim_i1 * v.shape[1]

     

    #H = H.reshape(dim,dim)
    #print "     Size of Hamitonian block: ", H.shape
=======
>>>>>>> master:nbody-hbuild.py
    return H.diagonal()
    # }}}

#def form_compressed_hamiltonian_diag(vecs,Hi,Hij,Szi,ms):
def form_compressed_hamiltonian_diag(vecs,Hi,Hij):
    # {{{
    dim = 1 # dimension of subspace
    dims = [] # list of mode dimensions (size of hilbert space on each fragment) 
    for vi,v in enumerate(vecs):
        dim = dim*v.shape[1]
        dims.extend([v.shape[1]])
    H = np.zeros((dim,dim))
    #Htest = np.zeros((dim,dim))
    n_dims = len(dims)


    H1 = cp.deepcopy(Hi)
    H2 = cp.deepcopy(Hij)
    for vi,v in enumerate(vecs):
        H1[vi] = np.dot(v.transpose(),np.dot(Hi[vi],v))

    for vi,v in enumerate(vecs):
        for wi,w in enumerate(vecs):
            if wi>vi:
                vw = np.kron(v,w)
                H2[(vi,wi)] = np.dot(vw.transpose(),np.dot(Hij[(vi,wi)],vw))
    
    dimsdims = dims
    dimsdims = np.append(dims,dims)

    #Htest = Htest.reshape(dimsdims)
    #   Add up all the one-body contributions, making sure that the results is properly dimensioned for the 
    #   target subspace
    dim_i1=1 #   dimension of space to the left
    dim_i2=dim #   dimension of space to the right
    
    for vi,v in enumerate(vecs):
        i1 = np.eye(dim_i1)
        dim_i2 = dim_i2/v.shape[1]
        i2 = np.eye(dim_i2)
        
        #print "dim_i1  :  dim_i2", dim_i1, dim_i2, dim
        H += np.kron(i1,np.kron(H1[vi],i2))
        
        #nv = v.shape[1]
        #test = np.ones(len(dimsdims)).astype(int)
        #test[vi] = nv
        #test[vi+len(dims)] = nv
        
        #h = cp.deepcopy(H1[vi])
        #h = h.reshape(test)
        #Htest = np.einsum('ijkljk->ijklmn',Htest,h)
        
        dim_i1 = dim_i1 * v.shape[1]

     
    #   Add up all the two-body contributions, making sure that the results is properly dimensioned for the 
    #   target subspace
    dim_i1=1 #   dimension of space to the left
    dim_i2=1 #   dimension of space in the middle 
    dim_i2=dim #   dimension of space to the right
  
    H = H.reshape(dimsdims)

    for vi,v in enumerate(vecs):
        for wi,w in enumerate(vecs):
            if wi>vi:

                nv = v.shape[1]
                nw = w.shape[1]
                dim_env = dim / nv / nw
                #print ": ", nv, nw, dim_env, dim
                
    
                i1 = np.eye(dim_env)
                h = np.kron(H2[(vi,wi)],i1)
                #print ": ", H2[(vi,wi)].shape, i1.shape, h.shape, H.shape
                
                #print H2[(vi,wi)].shape, " x ", i1.shape, " = ", h.shape
                
                tens_dims    = []
                tens_inds    = []
                tens_inds.extend([vi])
                tens_inds.extend([wi])
                tens_dims.extend([nv])
                tens_dims.extend([nw])
                for ti,t in enumerate(vecs):
                    if (ti != vi) and (ti != wi):
                        tens_dims.extend([t.shape[1]])
                        tens_inds.extend([ti])
                tens_dims = np.append(tens_dims, tens_dims) 
                #tens_inds = np.append(tens_inds, tens_inds) 

                sort_ind = np.argsort(tens_inds)
                
                swap = np.append(sort_ind,sort_ind+n_dims) 

                #todo and check
                #h.shape = (tens_dims)
                #H += h.transpose(swap)
                H += h.reshape(tens_dims).transpose(swap)
                
    H = H.reshape(dim,dim)
<<<<<<< HEAD:deprecated/nbody-hbuild.py

    ## Project this onto m_s = 0 (or other target)
    #Sz = form_compressed_zero_order_hamiltonian_diag(vecs0,Szi)# This is the diagonal of Sz in the current space
    #H = filter_rows_cols(H, Szi, Sz0_0, target_ms)

    #print "     Size of Hamitonian block: ", H.shape
=======
    #printm(H)
>>>>>>> master:nbody-hbuild.py
    return H
    # }}}

def form_compressed_hamiltonian_offdiag_1block_diff(vecs_l,vecs_r,Hi,Hij,differences):
    # {{{
    """
        Find (1-site) Hamiltonian matrix in between differently compressed spaces:
            i.e., 
                <Abcd| H(1) |ab'c'd'> = <A|Ha|a> * del(bb') * del(cc')
            or like,
                <aBcd| H(1) |abcd> = <B|Hb|b> * del(aa') * del(cc')
        
        Notice that the full Hamiltonian will also have the two-body part:
            <Abcd| H(2) |abcd> = <Ab|Hab|ab'> del(cc') + <Ac|Hac|ac'> del(bb')

       
        differences = [blocks which are not diagonal]
            i.e., for <Abcd|H(1)|abcd>, differences = [1]
                  for <Abcd|H(1)|aBcd>, differences = [1,2], and all values are zero for H(1)
            
        vecs_l  [vecs_A, vecs_B, vecs_C, ...]
        vecs_r  [vecs_A, vecs_B, vecs_C, ...]
    """
    dim_l = 1 # dimension of left subspace
    dim_r = 1 # dimension of right subspace
    dim_same = 1 # dimension of space spanned by all those fragments is the same space (i.e., not the blocks inside differences)
    dims_l = [] # list of mode dimensions (size of hilbert space on each fragment) 
    dims_r = [] # list of mode dimensions (size of hilbert space on each fragment) 
  
    
    block_curr = differences[0] # current block which is offdiagonal

    #   vecs_l correspond to the bra states
    #   vecs_r correspond to the ket states


    assert(len(vecs_l) == len(vecs_r))
    

    for bi,b in enumerate(vecs_l):
        dim_l = dim_l*b.shape[1]
        dims_l.extend([b.shape[1]])
        if bi !=block_curr:
            dim_same *= b.shape[1]

    dim_same_check = 1
    for bi,b in enumerate(vecs_r):
        dim_r = dim_r*b.shape[1]
        dims_r.extend([b.shape[1]])
        if bi !=block_curr:
            dim_same_check *= b.shape[1]

    assert(dim_same == dim_same_check)

    H = np.zeros((dim_l,dim_r))
<<<<<<< HEAD:deprecated/nbody-hbuild.py
    #print "     Size of Hamitonian block: ", H.shape
=======
>>>>>>> master:nbody-hbuild.py

    assert(len(dims_l) == len(dims_r))
    n_dims = len(dims_l)


    H1 = cp.deepcopy(Hi)
    H2 = cp.deepcopy(Hij)
    
    ## Rotate the single block Hamiltonians into the requested single site basis 
    #for vi in range(0,n_dims):
    #    l = vecs_l[vi]
    #    r = vecs_r[vi]
    #    H1[vi] = l.T.dot(Hi[vi]).dot(r)

    # Rotate the double block Hamiltonians into the appropriate single site basis 
#    for vi in range(0,n_dims):
#        for wi in range(0,n_dims):
#            if wi>vi:
#                vw_l = np.kron(vecs_l[vi],vecs_l[wi])
#                vw_r = np.kron(vecs_r[vi],vecs_r[wi])
#                H2[(vi,wi)] = vw_l.T.dot(Hij[(vi,wi)]).dot(vw_r)
   

    dimsdims = np.append(dims_l,dims_r) # this is the tensor layout for the many-body Hamiltonian in the current subspace
    
    vecs = vecs_l
    dims = dims_l
    dim = dim_l
    
    #   Add up all the one-body contributions, making sure that the results is properly dimensioned for the 
    #   target subspace
    dim_i1=1 # dimension of space for fragments to the left of the current 'different' fragment
    dim_i2=1 # dimension of space for fragments to the right of the current 'different' fragment

   
    # <abCdef|H1|abcdef> = eye(a) x eye(b) x <C|H1|c> x eye(d) x eye(e) x eye(f)
    for vi in range(n_dims):
        if vi<block_curr:
            dim_i1 *= dims_l[vi]
            assert(dims_l[vi]==dims_r[vi])
        elif vi>block_curr:
            dim_i2 *= dims_l[vi]
            assert(dims_l[vi]==dims_r[vi])
   
    # Rotate the current single block Hamiltonian into the requested single site basis 
    l = vecs_l[block_curr]
    r = vecs_r[block_curr]
    
    h1_block  = l.T.dot(Hi[block_curr]).dot(r)

    i1 = np.eye(dim_i1)
    i2 = np.eye(dim_i2)
    H += np.kron(i1,np.kron(h1_block,i2))

    # <abCdef|H2(0,2)|abcdef> = <aC|H2|ac> x eye(b) x eye(d) x eye(e) x eye(f) = <aCbdef|H2|acbdef>
    #
    #   then transpose:
    #       flip Cb and cb
    H.shape = (dims_l+dims_r)

    for bi in range(0,block_curr):
        #print "block_curr, bi", block_curr, bi
        vw_l = np.kron(vecs_l[bi],vecs_l[block_curr])
        vw_r = np.kron(vecs_r[bi],vecs_r[block_curr])
        h2 = vw_l.T.dot(Hij[(bi,block_curr)]).dot(vw_r) # i.e.  get reference to <aC|Hij[0,2]|a'c>, where block_curr = 2 and bi = 0

        dim_i = dim_same / dims[bi]
        #i1 = np.eye(dim_i)

        #tmp_h2 = np.kron( h2, i1)
        h2.shape = (dims_l[bi],dims_l[block_curr], dims_r[bi],dims_r[block_curr])
        
        tens_inds = []
        tens_inds.extend([bi,block_curr])
        tens_inds.extend([bi+n_dims,block_curr+n_dims])
        for bbi in range(0,n_dims):
            if bbi != bi and bbi != block_curr:
                tens_inds.extend([bbi])
                tens_inds.extend([bbi+n_dims])
                #print "h2.shape", h2.shape,
                h2 = np.tensordot(h2,np.eye(dims[bbi]),axes=0)
   
        #print "h2.shape", h2.shape,
        sort_ind = np.argsort(tens_inds)
        H += h2.transpose(sort_ind)
        #print "tens_inds", tens_inds
        #print "sort_ind", sort_ind 
        #print "h2", h2.transpose(sort_ind).shape
        #H += h2
    
    for bi in range(block_curr, n_dims):
        if bi == block_curr:
            continue
        #print "block_curr, bi", block_curr, bi
        vw_l = np.kron(vecs_l[block_curr],vecs_l[bi])
        vw_r = np.kron(vecs_r[block_curr],vecs_r[bi])
        h2 = vw_l.T.dot(Hij[(block_curr,bi)]).dot(vw_r) # i.e.  get reference to <aC|Hij[0,2]|a'c>, where block_curr = 2 and bi = 0

        h2.shape = (dims_l[block_curr],dims_l[bi], dims_r[block_curr],dims_r[bi])
        
        tens_inds = []
        tens_inds.extend([block_curr,bi])
        tens_inds.extend([block_curr+n_dims,bi+n_dims])
        for bbi in range(0,n_dims):
            if bbi != bi and bbi != block_curr:
                tens_inds.extend([bbi])
                tens_inds.extend([bbi+n_dims])
                #print "h2.shape", h2.shape,
                h2 = np.tensordot(h2,np.eye(dims[bbi]),axes=0)
   
        #print "h2.shape", h2.shape,
        sort_ind = np.argsort(tens_inds)
        #print "h2", h2.transpose(sort_ind).shape
        #print "tens_inds", tens_inds
        #print "sort_ind", sort_ind 
        H += h2.transpose(sort_ind)
        #print "h2.shape", h2.shape
    
    H.shape = (dim_l,dim_r)

    
    return H
    # }}}

def form_compressed_hamiltonian_offdiag_2block_diff(vecs_l,vecs_r,Hi,Hij,differences):
    # {{{
    """
        Find Hamiltonian matrix in between differently compressed spaces:
            i.e., 
                <Abcd| H(0,2) |a'b'C'd'> = <Ac|Ha|a'C'> * del(bb')
        
       
        differences = [blocks which are not diagonal]
            i.e., for <Abcd|H(1)|abCd>, differences = [0,2]
            
        vecs_l  [vecs_A, vecs_B, vecs_C, ...]
        vecs_r  [vecs_A, vecs_B, vecs_C, ...]
    """
    dim_l = 1 # dimension of left subspace
    dim_r = 1 # dimension of right subspace
    dim_same = 1 # dimension of space spanned by all those fragments is the same space (i.e., not the blocks inside differences)
    dims_l = [] # list of mode dimensions (size of hilbert space on each fragment) 
    dims_r = [] # list of mode dimensions (size of hilbert space on each fragment) 
  
    assert( len(differences) == 2) # make sure we are not trying to get H(1) between states with multiple fragments orthogonal 
    
    block_curr1 = differences[0] # current block which is offdiagonal
    block_curr2 = differences[1] # current block which is offdiagonal

    #   vecs_l correspond to the bra states
    #   vecs_r correspond to the ket states

    assert(len(vecs_l) == len(vecs_r))
    

    for bi,b in enumerate(vecs_l):
        dim_l = dim_l*b.shape[1]
        dims_l.extend([b.shape[1]])
        if bi !=block_curr1 and bi != block_curr2:
            dim_same *= b.shape[1]

    dim_same_check = 1
    for bi,b in enumerate(vecs_r):
        dim_r = dim_r*b.shape[1]
        dims_r.extend([b.shape[1]])
        if bi !=block_curr1 and bi != block_curr2:
            dim_same_check *= b.shape[1]

    assert(dim_same == dim_same_check)

    H = np.zeros((dim_l,dim_r))
<<<<<<< HEAD:deprecated/nbody-hbuild.py
    #print "     Size of Hamitonian block: ", H.shape
=======
>>>>>>> master:nbody-hbuild.py

    assert(len(dims_l) == len(dims_r))
    n_dims = len(dims_l)



    dimsdims = np.append(dims_l,dims_r) # this is the tensor layout for the many-body Hamiltonian in the current subspace
    
    #   Add up all the one-body contributions, making sure that the results is properly dimensioned for the 
    #   target subspace
    dim_i1=1 # dimension of space for fragments to the left of the current 'different' fragment
    dim_i2=1 # dimension of space for fragments to the right of the current 'different' fragment

   

    # <Abcdef|H2(0,2)|abCdef> = <Ac|H2|aC> x eye(b) x eye(d) x eye(e) x eye(f) = <aCbdef|H2|acbdef>
    #
    #   then transpose:
    #       flip Cb and cb
    H.shape = (dims_l+dims_r)

    #print block_curr1, block_curr2
    #assert(block_curr1 < block_curr2)

    #print " block_curr1, block_curr2", block_curr1, block_curr2
    vw_l = np.kron(vecs_l[block_curr1],vecs_l[block_curr2])
    vw_r = np.kron(vecs_r[block_curr1],vecs_r[block_curr2])
    h2 = vw_l.T.dot(Hij[(block_curr1,block_curr2)]).dot(vw_r) # i.e.  get reference to <aC|Hij[0,2]|a'c>, where block_curr = 2 and bi = 0

    h2.shape = (dims_l[block_curr1],dims_l[block_curr2], dims_r[block_curr1],dims_r[block_curr2])
    
    tens_inds = []
    tens_inds.extend([block_curr1,block_curr2])
    tens_inds.extend([block_curr1+n_dims,block_curr2+n_dims])
    for bbi in range(0,n_dims):
        if bbi != block_curr1 and bbi != block_curr2:
            tens_inds.extend([bbi])
            tens_inds.extend([bbi+n_dims])
            #print "h2.shape", h2.shape,

            assert(dims_l[bbi] == dims_r[bbi])
            dims = dims_l
            h2 = np.tensordot(h2,np.eye(dims[bbi]),axes=0)
   
    #print "h2.shape", h2.shape,
    sort_ind = np.argsort(tens_inds)
    H += h2.transpose(sort_ind)
    #print "tens_inds", tens_inds
    #print "sort_ind", sort_ind 
    #print "h2", h2.transpose(sort_ind).shape
    #H += h2
    
    H.shape = (dim_l,dim_r)

    
    return H
    # }}}

def assemble_blocked_matrix(H_sectors,n_blocks,n_body_order):
    #{{{
    Htest = np.array([])


    if n_body_order == 0:
        Htest = H_sectors[0,0]

    if n_body_order == 1:
        Htest = H_sectors[0,0]
        # Singles
        for bi in range(n_blocks+1):
            row_i = np.array([])
            
            for bj in range(n_blocks+1):
                if bj == 0:
                    row_i = H_sectors[bi,bj]
                else:
                    row_i = np.hstack((row_i,H_sectors[bi,bj]))
            
            if bi == 0:
                Htest = row_i
            else:
                Htest = np.vstack((Htest,row_i))
    
    
    if n_body_order == 2:
        
        #
        #   Get dimensionality
        #
        n0 = 0
        n1 = 0
        n2 = 0

        n0 = H_sectors[0,0].shape[0]
        for bi in range(1,n_blocks+1):
            n1 += H_sectors[bi,bi].shape[0]
        for bi in range(1,n_blocks+1):
            for bj in range(bi+1,n_blocks+1):
                n2 += H_sectors[(bi,bj),(bi,bj)].shape[0]

        nd = n0 + n1 + n2

<<<<<<< HEAD:deprecated/nbody-hbuild.py
=======
        #print "Dimensions: ", n0, n1, n2, " = ", nd

>>>>>>> master:nbody-hbuild.py
        Htest = np.empty([nd,nd])

        row = np.empty([n0,nd])
        
        # 0,0 


        col_start = 0
        
        col_stop = col_start + n0
        row[0::,col_start:col_stop] = H_sectors[0,0]
        col_start = col_stop

        #row_0 = H_sectors[0,0]
        # 0,S
        for bi in range(1,n_blocks+1):
            #row = np.hstack( ( row_0, H_sectors[0,bi] ) )

            col_stop = col_start + H_sectors[0,bi].shape[1]
            
            row[0::,col_start:col_stop] = H_sectors[0,bi]

            col_start = col_stop
            #row_0 = np.hstack( ( row_0, H_sectors[0,bi] ) )
        # 0,D
        for bi in range(1,n_blocks+1):
            for bj in range(bi+1, n_blocks+1):
                bij = (bi,bj)
                #print row_0.shape, H_sectors[0,bij].shape
                
                #row_0 = np.hstack( ( row_0, H_sectors[0,(bi,bj)] ) )
                
                col_stop = col_start + H_sectors[0,bij].shape[1]
                row[0::,col_start:col_stop] = H_sectors[0,bij]
                col_start = col_stop
    
    
        row_start = 0
        row_stop  = row_start + n0
        
        Htest[row_start:row_stop,0::] = row
        #Htest[row_start:row_stop,0::] = row_0 
       
        row_start = row_stop
        
        
        
        # Singles
        for bi in range(1,n_blocks+1):
            
            col_start = 0
            
            row_stop = row_start + H_sectors[bi,0].shape[0]
            
            row = np.empty([row_stop-row_start,nd])

            # bi,0
            col_stop = col_start + H_sectors[bi,0].shape[1]
            row[0::,col_start:col_stop] = H_sectors[bi,0]
            col_start = col_stop
            
            #row_i = H_sectors[bi,0] 
            
            # bi,bj 
            for bj in range(1,n_blocks+1):
                col_stop = col_start + H_sectors[bi,bj].shape[1]
                row[0::,col_start:col_stop] = H_sectors[bi,bj]
                col_start = col_stop
                
                #row_i = np.hstack((row_i,H_sectors[bi,bj]))
            # bi,bjk 
            for bj in range(1,n_blocks+1):
                for bk in range(bj+1,n_blocks+1):
                    col_stop = col_start + H_sectors[bi,(bj,bk)].shape[1]
                    row[0::,col_start:col_stop] = H_sectors[bi,(bj,bk)]
                    col_start = col_stop
                
                    #row_i = np.hstack((row_i,H_sectors[bi,(bj,bk)]))
            
            #Htest = np.vstack((Htest,row_i))
           
                
            Htest[row_start:row_stop,0::] = row 
            #Htest[row_start:row_stop,0::] = row_i 
    
            row_start = row_stop
    
        
        
    
        #Doubles 
        for bi in range(1,n_blocks+1):
            for bj in range(bi+1,n_blocks+1):
            
                col_start = 0
        
            
                bij = (bi,bj)

                row_stop = row_start + H_sectors[bij,0].shape[0]
            
                row = np.empty([row_stop-row_start,nd])

                # bij,0
                col_stop = col_start + H_sectors[bij,0].shape[1]
                row[0::,col_start:col_stop] = H_sectors[bij,0]
                col_start = col_stop
            
                #row_ij = H_sectors[(bi,bj),0]                                       #<ij|H|0>
                # bij,bk
                for bk in range(1,n_blocks+1):
                    col_stop = col_start + H_sectors[bij,bk].shape[1]
                    row[0::,col_start:col_stop] = H_sectors[bij,bk]
                    col_start = col_stop
            
                    #row_ij = np.hstack( (row_ij, H_sectors[(bi,bj),bk]) )           #<ij|H|k>
                # bij,bkl
                for bk in range(1,n_blocks+1):
                    for bl in range(bk+1,n_blocks+1):
                        bkl = (bk,bl)

                        col_stop = col_start + H_sectors[bij,bkl].shape[1]
                        row[0::,col_start:col_stop] = H_sectors[bij,bkl]
                        col_start = col_stop
            
                        #row_ij = np.hstack( (row_ij, H_sectors[(bi,bj),(bk,bl)]) )  #<ij|H|kl>
                
                #Htest = np.vstack((Htest,row_ij))
                
                Htest[row_start:row_stop,0::] = row
                #Htest[row_start:row_stop,0::] = row_ij 
    
                row_start = row_stop

    return Htest
    #}}}

def filter_rows_cols(A, sz_r, sz_c, sz):
    #{{{
    """
    Filter the matrix A by keeping only the rows and columns for which sz_r(r) = sz and sz_c(c) = sz

    This is used to grab only the portion of the Hamiltonian which has constant s_z
    """
    r_list = np.array([],dtype=int)
    c_list = np.array([],dtype=int)
    thresh = 1e-8
    for r in range(0,A.shape[0]):
        if abs(sz_r[r] - sz) < thresh:
            r_list = np.hstack((r_list,r))
    for c in range(0,A.shape[1]):
        if abs(sz_c[c] - sz) < thresh:
            c_list = np.hstack((c_list,c))
            #c_list.extend([c])

    return A[r_list,::][::,c_list]
    #}}}

def get_ms_subspace_list(v, Szi, ms):
    #{{{
    """
    Get a list of configurations with requested m_s value

    The current space is defined by the vectors in v (i.e., a list of all compression vectors on each fragment)

    Szi is just the Sz matrix for each fragment
    """
    Sz0 = form_compressed_zero_order_hamiltonian_diag(v,Szi)# <vvv..|Sz|vvv..>
    
    r_list = np.array([],dtype=int)
    thresh = 1e-12
    for r in range(0,Sz0.shape[0]):
        if abs(Sz0[r] - ms) < thresh:
            r_list = np.hstack((r_list,r))

    #print "r_list ", Sz0 
    #print "r_list ", r_list
    return r_list
    #}}}

def get_ms_subspace_list2(v, Szi, Szij, ms):
    #{{{
    """
    Get a list of configurations with requested m_s value

    The current space is defined by the vectors in v (i.e., a list of all compression vectors on each fragment)

    Szi is just the Sz matrix for each fragment
    """
    Sz0  = form_compressed_hamiltonian_diag(v,Szi,Szij) # <QPQ|H|QPQ>

    r_list = np.array([],dtype=int)
    thresh = 1e-12
    for r in range(0,Sz0.shape[0]):
        if abs(Sz0[r,r] - ms) < thresh:
        #if np.isclose(Sz0[r,r], ms):
            r_list = np.hstack((r_list,r))

    #print "r_list ", Sz0 
    #print "r_list ", r_list
    return r_list
    #}}}





"""
Test forming HDVV Hamiltonian and projecting onto "many-body tucker basis"
"""
#   Setup input arguments
parser = argparse.ArgumentParser(description='Finds eigenstates of a spin lattice',
formatter_class=argparse.ArgumentDefaultsHelpFormatter)

#parser.add_argument('-d','--dry_run', default=False, action="store_true", help='Run but don\'t submit.', required=False)
parser.add_argument('-ju','--j_unit', type=str, default="cm", help='What units are the J values in', choices=['cm','ev'],required=False)
parser.add_argument('-l','--lattice', type=str, default="heis_lattice.m", help='File containing vector of sizes number of electrons per lattice site', required=False)
parser.add_argument('-j','--j12', type=str, default="heis_j12.m", help='File containing matrix of exchange constants', required=False)
parser.add_argument('-b','--blocks', type=str, default="heis_blocks.m", help='File containing vector of block sizes', required=False)
#parser.add_argument('-s','--save', default=False, action="store_true", help='Save the Hamiltonian and S2 matrices', required=False)
#parser.add_argument('-r','--read', default=False, action="store_true", help='Read the Hamiltonian and S2 matrices', required=False)
#parser.add_argument('-hdvv','--hamiltonian', type=str, default="heis_hamiltonian.npy", help='File containing matrix of Hamiltonian', required=False)
#parser.add_argument('-s2','--s2', type=str, default="heis_s2.npy", help='File containing matrix of s2', required=False)
#parser.add_argument('--eigvals', type=str, default="heis_eigvals.npy", help='File of Hamiltonian eigvals', required=False)
#parser.add_argument('--eigvecs', type=str, default="heis_eigvecs.npy", help='File of Hamiltonian eigvecs', required=False)
parser.add_argument('-np','--n_p_space', type=int, nargs="+", help='Number of vectors in block P space', required=False)
parser.add_argument('-nq','--n_q_space', type=int, nargs="+", help='Number of vectors in block Q space', required=False)
parser.add_argument('-nb','--n_body_order', type=int, default="0", help='n_body spaces', required=False)
parser.add_argument('-nr','--n_roots', type=int, default="10", help='Number of eigenvectors to find in compressed space', required=False)
parser.add_argument('--n_print', type=int, default="10", help='number of states to print', required=False)
parser.add_argument('--use_exact_tucker_factors', action="store_true", default=False, help='Use compression vectors from tucker decomposition of exact ground states', required=False)
parser.add_argument('-ts','--target_state', type=int, default="0", nargs='+', help='state(s) to target during (possibly state-averaged) optimization', required=False)
parser.add_argument('-mit', '--max_iter', type=int, default=50, help='Max iterations for solving for the compression vectors', required=False)
parser.add_argument('-thresh', type=int, default=8, help='Threshold for pspace iterations', required=False)
parser.add_argument('-pt','--pt_order', type=int, default=2, help='PT correction order ?', required=False)
parser.add_argument('-pt_type','--pt_type', type=str, default='mp', choices=['mp','en'], help='PT correction denominator type', required=False)
parser.add_argument('-ms','--target_ms', type=float, default=0, help='Target ms space', required=False)
parser.add_argument('-opt','--optimization', type=str, default="None", help='Optimization algorithm for Tucker factors',choices=["none", "diis"], required=False)
args = vars(parser.parse_args())
#
#   Let minute specification of walltime override hour specification

j12 = np.loadtxt(args['j12'])
lattice = np.loadtxt(args['lattice']).astype(int)
blocks = np.loadtxt(args['blocks']).astype(int)
n_sites = len(lattice)
n_blocks = len(blocks)
    
if len(blocks.shape) == 1:
    print 'blocks',blocks
    
    blocks.shape = (1,len(blocks.transpose()))
    n_blocks = len(blocks)


n_p_states = args['n_p_space'] 
n_q_states = args['n_q_space'] 


if args['n_p_space'] == None:
    n_p_states = []
    for bi in range(n_blocks):
        n_p_states.extend([1])
    args['n_p_space'] = n_p_states

assert(len(args['n_p_space']) == n_blocks)

np.random.seed(2)


au2ev = 27.21165;
au2cm = 219474.63;
convert = au2ev/au2cm;	# convert from wavenumbers to eV
convert = 1;			# 1 for wavenumbers

if args['j_unit'] == 'cm':
    j12 = j12 * au2ev/au2cm

print " j12:\n", j12
print " lattice:\n", lattice 
print " blocks:\n", blocks
print " n_blocks:\n", n_blocks

H_tot = np.array([])
S2_tot = np.array([])
H_dict = {}

#get Hamiltonian and eigenstates 
#if args['read']:
#    print "Reading Hamiltonian and S2 from disk"
#    H_tot = np.load(args['hamiltonian'])
#    S2_tot = np.load(args['s2'])
#    v = np.load(args['eigvecs'])
#    l = np.load(args['eigvals'])
#else:
#    print "Building Hamiltonian"
#    H_tot, H_dict, S2_tot, Sz_tot = form_hdvv_H(lattice,j12)


    #print " Diagonalize Hamiltonian (%ix%i):\n" %(H_tot.shape[0],H_tot.shape[0]), H_tot.shape
    #l,v = np.linalg.eigh(H_tot)
    #l,v = scipy.sparse.linalg.eigsh(H_tot, k=min(100,H_tot.shape[0]))



#if args['save']==True:
#    np.save("heis_hamiltonian",H_tot)
#    np.save("heis_s2",S2_tot)
#


#print v.shape
#print S2_tot.shape

#S2_eig = np.dot(v.transpose(),np.dot(S2_tot,v))
#print " %5s    %12s  %12s  %12s" %("State","Energy","Relative","<S2>")
#for si,i in enumerate(l):
#    print " %5i =  %12.8f  %12.8f  %12.8f" %(si,i*convert,(i-l[0])*convert,S2_eig[si,si])
#    if si>10:
#        break

#v0 = v[:,0]

#if args['save']==True:
#    np.save("heis_eigvecs",v)
#    np.save("heis_eigvals",l)
#




# reshape eigenvector into tensor
dims_tot = []
dim_tot = 1
for bi,b in enumerate(blocks):
    print "here:",b,bi
    block_dim = np.power(2,b.shape[0])
    dims_tot.extend([block_dim])
    dim_tot *= block_dim

if args['n_q_space'] == None:
    n_q_states = []
    for bi in range(n_blocks):
        n_q_states.extend([dims_tot[bi]-1])
    args['n_q_space'] = n_q_states

#v0 = np.reshape(v0,dims_tot)


# Get initial compression vectors 
p_states, q_states = get_guess_vectors(lattice, j12, blocks, n_p_states, n_q_states)

if args['use_exact_tucker_factors']:
    p_states = []
    q_states = []
    Acore, Atfac = tucker_decompose(v0,0,0)
    for bi,b in enumerate(Atfac):
        #p_states.extend([scipy.linalg.orth(np.random.rand(b.shape[0],n_p_states))])
        p_states.extend([b[:,0:n_p_states[bi]]])
        q_states.extend([b[:,n_p_states[bi]::]])

if 0:
    # do random guess
    p_states = []
    q_states = []
    for bi,b in enumerate(blocks):
        block_dim = np.power(2,b.shape[0])
        r = scipy.linalg.orth(np.random.rand(block_dim,block_dim))
        p_states.extend([r[:,0:n_p_states[bi]]])
        q_states.extend([r[:,n_p_states[bi]:n_p_states[bi]+n_q_states[bi]]])

dims_0 = n_p_states

#
# |Ia,Ib,Ic> P(Ia,a) P(Ib,b) P(Ic,c) = |abc>    : |PPP>
#
# |Ia,Ib,Ic> Q(Ia,A) P(Ib,b) P(Ic,c) = |Abc>    : |QPP>
# |Ia,Ib,Ic> P(Ia,a) Q(Ib,B) P(Ic,c) = |aBc>    : |PQP>
#
# |Ia,Ib,Ic> Q(Ia,A) Q(Ib,B) P(Ic,c) = |ABc>    : |QQP>
#
#<abc|Ha+Hb+Hc+Hab+Hac+Hbc|abc>
#
#<a|Ha|a><bc|bc> = <a|Ha|a>
#<ab|Hab|ab><c|c> = <ab|Hab|ab>
#<Abc|Hab|Abc> = <Ab|Hab|Ab>


Hi = {}
Hij = {}
S2i = {}
S2ij = {}
Szi = {}
Szij = {}
#1 body operators
for bi,b in enumerate(blocks):
    Hi[bi], S2i[bi], Szi[bi] = form_superblock_hamiltonian(lattice, j12, blocks, [bi])

#2 body operators
for bi,b in enumerate(blocks):
    for bj,bb in enumerate(blocks):
        if bj>bi:
            hi = Hi[bi]
            hj = Hi[bj]
            s2i = S2i[bi]
            s2j = S2i[bj]
            szi = Szi[bi]
            szj = Szi[bj]
            
            Hij[(bi,bj)], S2ij[(bi,bj)], Szij[(bi,bj)] = form_superblock_hamiltonian(lattice, j12, blocks, [bi,bj])
            Hij[(bi,bj)] -= np.kron(hi,np.eye(hj.shape[0])) 
            Hij[(bi,bj)] -= np.kron(np.eye(hi.shape[0]),hj) 


            S2ij[(bi,bj)] -= np.kron(s2i,np.eye(s2j.shape[0])) 
            S2ij[(bi,bj)] -= np.kron(np.eye(s2i.shape[0]),s2j) 
            Szij[(bi,bj)] -= np.kron(szi,np.eye(szj.shape[0])) 
            Szij[(bi,bj)] -= np.kron(np.eye(szi.shape[0]),szj) 





# loop over compression vector iterations
energy_per_iter = []
maxiter = args['max_iter'] 
last_vector = np.array([])  # used to detect root flipping

diis_err_vecs = {}
diis_frag_grams = {}

opt = args['optimization'] 

for bi in range(0,n_blocks):
    #diis_err_vecs[bi] = np.empty((p_states[bi].shape[0]* p_states[bi].shape[0],1))
    #diis_err_vecs[bi] = np.empty((q_states[bi].shape[1], 0))
    diis_err_vecs[bi] = np.array([])
    diis_frag_grams[bi] = []

for it in range(0,maxiter):


    print " Tucker optimization: Iteration %4i" %it

    vecs0 = []
    # get vecs for PPP class
    for bi,b in enumerate(blocks):
        vecs0.extend([p_states[bi]])
    
    vecsQ = []
    for bi in range(n_blocks):
        v = cp.deepcopy(vecs0)
        v[bi] = q_states[bi]
        vecsQ.extend([v])
    
    vecsQQ = {}
    for bi in range(n_blocks):
        for bj in range(bi+1,n_blocks):
            v = cp.deepcopy(vecs0)
            v[bi] = q_states[bi]
            v[bj] = q_states[bj]
            vecsQQ[bi,bj] = v
   
    count = {}

    H0_0 = form_compressed_hamiltonian_diag(vecs0,Hi,Hij)   # <PPP|H|PPP>
    S20_0 = form_compressed_hamiltonian_diag(vecs0,S2i,S2ij)# <PPP|S^2|PPP>
    #Sz0_0 = form_compressed_hamiltonian_diag(vecs0,Szi,Szij)# <PPP|S^2|PPP>
    #Sz0 = form_compressed_zero_order_hamiltonian_diag(vecs0,Szi)# <PPP|Sz|PPP>

    H_zero_order_diag =  np.array([]) 

    # Project this onto m_s = 0 (or other target)
    ms_proj = 0
    target_ms = args['target_ms']
    if ms_proj:
        ms_space_0 = get_ms_subspace_list2(vecs0, Szi, Szij, target_ms)
        #ms_space_0 = get_ms_subspace_list(vecs0, Szi, target_ms)
        
        H0_0 = H0_0[ms_space_0,::][::,ms_space_0]
        S20_0 = S20_0[ms_space_0,::][::,ms_space_0]
        #Sz0_0 = Sz0_0[ms_space_0,::][::,ms_space_0]
    
        #H_zero_order_diag = form_compressed_zero_order_hamiltonian_diag(vecsQ[bi],Hi) # <PPP|H|PPP>
    
    if args['pt_order'] > 0:
        H_zero_order_diag = form_compressed_zero_order_hamiltonian_diag(vecs0,Hi) # <PPP|H|PPP>
        if ms_proj:
            ms_space_0 = get_ms_subspace_list2(vecs0, Szi, Szij, target_ms)
        
            H_zero_order_diag = H_zero_order_diag[ms_space_0]

    
    #H0_0 = filter_rows_cols(H0_0, Sz0_0, Sz0_0, target_ms)
    #S20_0 = filter_rows_cols(S20_0, Sz0, Sz0, target_ms)
    #
    

    H_sectors = {}
    H_sectors[0,0] = H0_0
    
    S2_sectors = {}
    S2_sectors[0,0] = S20_0
    
    #Sz_sectors = {}
    #Sz_sectors[0,0] = Sz0_0
        
    n_body_order = args['n_body_order'] 
    
    if n_body_order >= 1:
        for bi in range(n_blocks):
            if args['pt_order'] > 0 and ms_proj == 0:
                H_zero_order_diag = np.hstack((H_zero_order_diag,
                    form_compressed_zero_order_hamiltonian_diag(vecsQ[bi],Hi)
                    ) )# <QPP|H|QPP>


            H_sectors[bi+1,bi+1]    = form_compressed_hamiltonian_diag(vecsQ[bi],Hi,Hij) # <QPP|H|QPP>
            
            H_sectors[0,bi+1]       = form_compressed_hamiltonian_offdiag_1block_diff(vecs0,vecsQ[bi],Hi,Hij,[bi]) # <PPP|H|QPP>
            H_sectors[bi+1,0]       = H_sectors[0,bi+1].T
            
            S2_sectors[bi+1,bi+1]    = form_compressed_hamiltonian_diag(vecsQ[bi],S2i,S2ij) # <QPP|H|QPP>
            S2_sectors[0,bi+1]       = form_compressed_hamiltonian_offdiag_1block_diff(vecs0,vecsQ[bi],S2i,S2ij,[bi]) # <PPP|H|QPP>
            S2_sectors[bi+1,0]       = S2_sectors[0,bi+1].T
            
            #Sz_sectors[bi+1,bi+1]    = form_compressed_hamiltonian_diag(vecsQ[bi],Szi,Szij) # <QPP|H|QPP>
            #Sz_sectors[0,bi+1]       = form_compressed_hamiltonian_offdiag_1block_diff(vecs0,vecsQ[bi],Szi,Szij,[bi]) # <PPP|H|QPP>
            #Sz_sectors[bi+1,0]       = Sz_sectors[0,bi+1].T
   
            # project each matrix onto target m_s space
            if ms_proj:
                ms_space_Pi = get_ms_subspace_list2(vecsQ[bi], Szi, Szij, target_ms)
                #ms_space_Pi = get_ms_subspace_list(vecsQ[bi], Szi, target_ms)
             
                H_sectors[bi+1,bi+1] = H_sectors[bi+1,bi+1][ms_space_Pi,::][::,ms_space_Pi]
                H_sectors[0   ,bi+1] = H_sectors[0   ,bi+1][ms_space_0 ,::][::,ms_space_Pi]
                H_sectors[bi+1,   0] = H_sectors[bi+1,   0][ms_space_Pi,::][::, ms_space_0]
                
                S2_sectors[bi+1,bi+1] = S2_sectors[bi+1,bi+1][ms_space_Pi,::][::,ms_space_Pi]
                S2_sectors[0   ,bi+1] = S2_sectors[0   ,bi+1][ms_space_0, ::][::,ms_space_Pi]
                S2_sectors[bi+1,   0] = S2_sectors[bi+1,   0][ms_space_Pi,::][::, ms_space_0]
                
                #Sz_sectors[bi+1,bi+1] = Sz_sectors[bi+1,bi+1][ms_space_Pi,::][::,ms_space_Pi]
                #Sz_sectors[0   ,bi+1] = Sz_sectors[0   ,bi+1][ms_space_0, ::][::,ms_space_Pi]
                #Sz_sectors[bi+1,   0] = Sz_sectors[bi+1,   0][ms_space_Pi,::][::, ms_space_0]
                if args['pt_order'] > 0:
                    H_zero_order_diag = np.hstack((H_zero_order_diag,
                            form_compressed_zero_order_hamiltonian_diag(vecsQ[bi],Hi)[ms_space_Pi]
                            ) )# <QPP|H|QPP>
        
    
            
            for bj in range(bi+1,n_blocks):
                H_sectors[bi+1,bj+1] = form_compressed_hamiltonian_offdiag_2block_diff(vecsQ[bi],vecsQ[bj],Hi,Hij,[bi,bj]) # <QPP|H|PQP>
                H_sectors[bj+1,bi+1] = H_sectors[bi+1,bj+1].T
    
                S2_sectors[bi+1,bj+1] = form_compressed_hamiltonian_offdiag_2block_diff(vecsQ[bi],vecsQ[bj],S2i,S2ij,[bi,bj]) # <QPP|H|PQP>
                S2_sectors[bj+1,bi+1] = S2_sectors[bi+1,bj+1].T
            
                #Sz_sectors[bi+1,bj+1] = form_compressed_hamiltonian_offdiag_2block_diff(vecsQ[bi],vecsQ[bj],Szi,Szij,[bi,bj]) # <QPP|H|PQP>
                #Sz_sectors[bj+1,bi+1] = Sz_sectors[bi+1,bj+1].T
            
                # project each matrix onto target m_s space
                if ms_proj:
                    ms_space_Pj = get_ms_subspace_list2(vecsQ[bj], Szi, Szij, target_ms)
                    #ms_space_Pj = get_ms_subspace_list(vecsQ[bj], Szi, target_ms)

                    H_sectors[bi+1,bj+1] = H_sectors[bi+1,bj+1][ms_space_Pi,::][::,ms_space_Pj]
                    H_sectors[bj+1,bi+1] = H_sectors[bj+1,bi+1][ms_space_Pj,::][::,ms_space_Pi]
                    S2_sectors[bi+1,bj+1] = S2_sectors[bi+1,bj+1][ms_space_Pi,::][::,ms_space_Pj]
                    S2_sectors[bj+1,bi+1] = S2_sectors[bj+1,bi+1][ms_space_Pj,::][::,ms_space_Pi]
                    #Sz_sectors[bi+1,bj+1] = Sz_sectors[bi+1,bj+1][ms_space_Pi,::][::,ms_space_Pj]
                    #Sz_sectors[bj+1,bi+1] = Sz_sectors[bj+1,bi+1][ms_space_Pj,::][::,ms_space_Pi]
            
            
    
   
    if n_body_order >= 2:
        for bi in range(n_blocks):
            for bj in range(bi+1,n_blocks):
                bij = (bi+1,bj+1)
                if args['pt_order'] > 0 and ms_proj == 0:
                    H_zero_order_diag = np.hstack((H_zero_order_diag,
                            form_compressed_zero_order_hamiltonian_diag(vecsQQ[bi,bj],Hi)
                            ) )# <QPP|H|QPP>
                print " Form Hamiltonian for <%s|H|%s>" %(bij, bij)
                H_sectors[bij,bij]  = form_compressed_hamiltonian_diag(vecsQQ[bi,bj],Hi,Hij) # <QPQ|H|QPQ>
                
                print " Form Hamiltonian for <%s|H|%s>" %(0, bij)
                H_sectors[0,bij]    = form_compressed_hamiltonian_offdiag_2block_diff(vecs0,vecsQQ[bi,bj],Hi,Hij,[bi,bj]) # <PPP|H|QQP>
                H_sectors[bij,0]    = H_sectors[0,bij].T
                
                S2_sectors[bij,bij]  = form_compressed_hamiltonian_diag(vecsQQ[bi,bj],S2i,S2ij) # <QPQ|H|QPQ>
                S2_sectors[0,bij]    = form_compressed_hamiltonian_offdiag_2block_diff(vecs0,vecsQQ[bi,bj],S2i,S2ij,[bi,bj]) # <PPP|H|QQP>
                S2_sectors[bij,0]    = S2_sectors[0,bij].T
                
                #Sz_sectors[bij,bij]  = form_compressed_hamiltonian_diag(vecsQQ[bi,bj],Szi,Szij) # <QPQ|H|QPQ>
                #Sz_sectors[0,bij]    = form_compressed_hamiltonian_offdiag_2block_diff(vecs0,vecsQQ[bi,bj],Szi,Szij,[bi,bj]) # <PPP|H|QQP>
                #Sz_sectors[bij,0]    = Sz_sectors[0,bij].T
            
                # project each matrix onto target m_s space
                if ms_proj:
                    ms_space_Pij = get_ms_subspace_list2(vecsQQ[bi,bj], Szi, Szij, target_ms)
                    #ms_space_Pij = get_ms_subspace_list(vecsQQ[bi,bj], Szi, target_ms)
                
                    H_sectors[bij,bij] = H_sectors[bij,bij][ms_space_Pij,::][::,ms_space_Pij]
                    H_sectors[0  ,bij] = H_sectors[0  ,bij][ms_space_0  ,::][::,ms_space_Pij]
                    H_sectors[bij,  0] = H_sectors[bij,  0][ms_space_Pij,::][::,  ms_space_0]
                 
                    S2_sectors[bij,bij] = S2_sectors[bij,bij][ms_space_Pij,::][::,ms_space_Pij]
                    S2_sectors[0  ,bij] = S2_sectors[0  ,bij][ms_space_0  ,::][::,ms_space_Pij]
                    S2_sectors[bij,  0] = S2_sectors[bij,  0][ms_space_Pij,::][::,  ms_space_0]
                    #Sz_sectors[bij,bij] = Sz_sectors[bij,bij][ms_space_Pij,::][::,ms_space_Pij]
                    #Sz_sectors[0  ,bij] = Sz_sectors[0  ,bij][ms_space_0  ,::][::,ms_space_Pij]
                    #Sz_sectors[bij,  0] = Sz_sectors[bij,  0][ms_space_Pij,::][::,  ms_space_0]
                    if args['pt_order'] > 0:
                        H_zero_order_diag = np.hstack((H_zero_order_diag,
                                form_compressed_zero_order_hamiltonian_diag(vecsQQ[bi,bj],Hi)[ms_space_Pij]
                                ) )# <QPP|H|QPP>
            
                
        for bi in range(n_blocks):
            for bj in range(bi+1,n_blocks):
                bij = (bi+1,bj+1)
                for bk in range(n_blocks):
                    if bk == bi:
                        print " Form Hamiltonian for <%s|H|%s>" %(bij, bk+1)
                        H_sectors[bk+1,bij]     = form_compressed_hamiltonian_offdiag_1block_diff(vecsQ[bk],vecsQQ[bi,bj],Hi,Hij,[bj]) # <PPQ|H|PQQ>
                        H_sectors[bij,bk+1]     = H_sectors[bk+1,bij].T
                        
                        S2_sectors[bk+1,bij]    = form_compressed_hamiltonian_offdiag_1block_diff(vecsQ[bk],vecsQQ[bi,bj],S2i,S2ij,[bj]) # <PPQ|H|PQQ>
                        S2_sectors[bij,bk+1]    = S2_sectors[bk+1,bij].T
                        
                        #Sz_sectors[bk+1,bij]    = form_compressed_hamiltonian_offdiag_1block_diff(vecsQ[bk],vecsQQ[bi,bj],Szi,Szij,[bj]) # <PPQ|H|PQQ>
                        #Sz_sectors[bij,bk+1]    = Sz_sectors[bk+1,bij].T
                    elif bk == bj:
                        print " Form Hamiltonian for <%s|H|%s>" %(bij, bk+1)
                        H_sectors[bk+1,bij]     = form_compressed_hamiltonian_offdiag_1block_diff(vecsQ[bk],vecsQQ[bi,bj],Hi,Hij,[bi]) # <PQP|H|PQQ>
                        H_sectors[bij,bk+1]     = H_sectors[bk+1,bij].T
                        
                        S2_sectors[bk+1,bij]    = form_compressed_hamiltonian_offdiag_1block_diff(vecsQ[bk],vecsQQ[bi,bj],S2i,S2ij,[bi]) # <PQP|H|PQQ>
                        S2_sectors[bij,bk+1]    = S2_sectors[bk+1,bij].T
                        
                        #Sz_sectors[bk+1,bij]    = form_compressed_hamiltonian_offdiag_1block_diff(vecsQ[bk],vecsQQ[bi,bj],Szi,Szij,[bi]) # <PQP|H|PQQ>
                        #Sz_sectors[bij,bk+1]    = Sz_sectors[bk+1,bij].T
                    else:
                        H_sectors[bk+1,bij]     = np.zeros( (H_sectors[bk+1,bk+1].shape[1] , H_sectors[bij,bij].shape[1] ) ) # <PQP|H|QPQ>
                        H_sectors[bij,bk+1]     = H_sectors[bk+1,bij].T
                
                        S2_sectors[bk+1,bij]    = np.zeros( (H_sectors[bk+1,bk+1].shape[1] , H_sectors[bij,bij].shape[1] ) ) # <PQP|H|QPQ>
                        S2_sectors[bij,bk+1]    = S2_sectors[bk+1,bij].T
                
                        #Sz_sectors[bk+1,bij]    = np.zeros( (H_sectors[bk+1,bk+1].shape[1] , H_sectors[bij,bij].shape[1] ) ) # <PQP|H|QPQ>
                        #Sz_sectors[bij,bk+1]    = Sz_sectors[bk+1,bij].T
            
                    # project each matrix onto target m_s space
                    if ms_proj:
                        if bk == bi or bk == bj :    #Zeros are already projected 
                            ms_space_Pij = get_ms_subspace_list2(vecsQQ[bi,bj], Szi, Szij, target_ms)
                            ms_space_Pk = get_ms_subspace_list2(vecsQ[bk], Szi, Szij, target_ms)
                            #ms_space_Pij = get_ms_subspace_list(vecsQQ[bi,bj], Szi, target_ms)
                            #ms_space_Pk = get_ms_subspace_list(vecsQ[bk], Szi, target_ms)
                    
                      
                            H_sectors[bk+1,bij] = H_sectors[bk+1,bij][ms_space_Pk,::][::,ms_space_Pij]
                            H_sectors[bij,bk+1] = H_sectors[bij,bk+1][ms_space_Pij,::][::,ms_space_Pk]
                            
                            S2_sectors[bij,bk+1] = S2_sectors[bij,bk+1][ms_space_Pij,::][::,ms_space_Pk]
                            S2_sectors[bk+1,bij] = S2_sectors[bk+1,bij][ms_space_Pk,::][::,ms_space_Pij]
                            
                            #Sz_sectors[bij,bk+1] = Sz_sectors[bij,bk+1][ms_space_Pij,::][::,ms_space_Pk]
                            #Sz_sectors[bk+1,bij] = Sz_sectors[bk+1,bij][ms_space_Pk,::][::,ms_space_Pij]
                    
                #for bk in range(bi,n_blocks):
                    for bl in range(bk+1,n_blocks):
                        bkl = (bk+1,bl+1)
    
                        #only compute upper triangular blocks
                        if bk < bi:
                            continue
                        if bk == bi and bl <= bj:
                            continue
                       
                        #count[(bij,bkl)] += 1
                        diff = {}
                        diff[bi] = 1
                        diff[bj] = 1
                        diff[bk] = 1
                        diff[bl] = 1
                        for bbi in (bi,bj):
                            for bbj in (bk,bl):
                                if bbi == bbj:
                                    diff[bbi] = 0
                        diff2 = []
                        for bbi in sorted(diff.keys()):     #added this sort after the fact, not completely sure this is not going to cause problems
                            if diff[bbi] == 1:
                                diff2.extend([bbi])
                       
                        if len(diff2) == 2:
                            print " Form Hamiltonian for <%s|H|%s>" %(bij, bkl)
                            H_sectors[bij,bkl]  = form_compressed_hamiltonian_offdiag_2block_diff(vecsQQ[bi,bj],vecsQQ[bk,bl],Hi,Hij,diff2) # <QPQ|H|QQP>
                            H_sectors[bkl,bij]  = H_sectors[bij,bkl].T
                            
                            S2_sectors[bij,bkl] = form_compressed_hamiltonian_offdiag_2block_diff(vecsQQ[bi,bj],vecsQQ[bk,bl],S2i,S2ij,diff2) # <QPQ|H|QQP>
                            S2_sectors[bkl,bij] = S2_sectors[bij,bkl].T
                            
                            #Sz_sectors[bij,bkl] = form_compressed_hamiltonian_offdiag_2block_diff(vecsQQ[bi,bj],vecsQQ[bk,bl],Szi,Szij,diff2) # <QPQ|H|QQP>
                            #Sz_sectors[bkl,bij] = Sz_sectors[bij,bkl].T
                        if len(diff2) > 2:
                            H_sectors[bij,bkl]  = np.zeros( (H_sectors[0,bij].shape[1] , H_sectors[0,bkl].shape[1] ) )
                            H_sectors[bkl,bij]  = H_sectors[bij,bkl].T
                            
                            S2_sectors[bij,bkl] = np.zeros( (H_sectors[0,bij].shape[1] , H_sectors[0,bkl].shape[1] ) )
                            S2_sectors[bkl,bij] = S2_sectors[bij,bkl].T
                            
                            #Sz_sectors[bij,bkl] = np.zeros( (H_sectors[0,bij].shape[1] , H_sectors[0,bkl].shape[1] ) )
                            #Sz_sectors[bkl,bij] = Sz_sectors[bij,bkl].T
                 
                        # project each matrix onto target m_s space
                        if ms_proj:
                            if len(diff2) == 2:   #Zeros are already projected 
                                ms_space_Pij = get_ms_subspace_list2(vecsQQ[bi,bj], Szi, Szij, target_ms)
                                ms_space_Pkl = get_ms_subspace_list2(vecsQQ[bk,bl], Szi, Szij, target_ms)
                                #ms_space_Pij = get_ms_subspace_list(vecsQQ[bi,bj], Szi, target_ms)
                                #ms_space_Pkl = get_ms_subspace_list(vecsQQ[bk,bl], Szi, target_ms)
                    
                             
                                H_sectors[bij,bkl] = H_sectors[bij,bkl][ms_space_Pij,::][::,ms_space_Pkl]
                                H_sectors[bkl,bij] = H_sectors[bkl,bij][ms_space_Pkl,::][::,ms_space_Pij]
                             
                                S2_sectors[bij,bkl] = S2_sectors[bij,bkl][ms_space_Pij,::][::,ms_space_Pkl]
                                S2_sectors[bkl,bij] = S2_sectors[bkl,bij][ms_space_Pkl,::][::,ms_space_Pij]
                             
                                #Sz_sectors[bij,bkl] = Sz_sectors[bij,bkl][ms_space_Pij,::][::,ms_space_Pkl]
                                #Sz_sectors[bkl,bij] = Sz_sectors[bkl,bij][ms_space_Pkl,::][::,ms_space_Pij]

    
    
    Htest = assemble_blocked_matrix(H_sectors, n_blocks, n_body_order) 
    S2test = assemble_blocked_matrix(S2_sectors, n_blocks, n_body_order) 
    #Sztest = assemble_blocked_matrix(Sz_sectors, n_blocks, n_body_order) 

    #print Sztest
   
    #r_list = np.array([],dtype=int)
    #sz_thresh = 1e-3
    #for r in range(0,Sztest.shape[0]):
    #    if abs(Sztest[r,r] - target_ms) < sz_thresh:
    #        r_list = np.hstack((r_list,r))
  
    #Htest_ms = Htest[r_list,::][::,r_list]
    #S2test_ms = S2test[r_list,::][::,r_list]
    #Sztest_ms = S2test[r_list,::][::,r_list]

    #print " Dimensions of Full Hamiltonian      ", H_tot.shape
    print " Dimensions of Subspace Hamiltonian  ", Htest.shape

    lp = np.array([])
    vp = np.array([])

    if Htest.shape[0] > 3000:
        lp,vp = scipy.sparse.linalg.eigsh(Htest, k=args["n_roots"] )
        #lp,vp = scipy.sparse.linalg.eigsh(Htest + Sztest, k=args["n_roots"] )
        pass
    else:
        #lp,vp = np.linalg.eigh(Htest_ms)
        #lp,vp = np.linalg.eigh(Htest)
        lp,vp = np.linalg.eigh(Htest)
 
    
    lp = vp.T.dot(Htest).dot(vp).diagonal()
            
    sort_ind = np.argsort(lp)
    lp = lp[sort_ind]
    vp = vp[:,sort_ind]

    s2 = vp.T.dot(S2test).dot(vp)
    #print 
    #print " Eigenvectors of compressed Hamiltonian"
    #print " %5s    %12s  %12s  %12s" %("State","Energy","Relative","<S2>")
    #for si,i in enumerate(lp):
    #    print " %5i =  %12.8f  %12.8f  %12.8f" %(si,i*convert,(i-lp[0])*convert,s2[si,si])
    #    if si>10:
    #        break
    
    target_state = args['target_state'] 

    #vpt = np.zeros((Htest.shape[0],vp.shape[1]))
    #vpt[r_list] = vp
    #vp = cp.deepcopy(vpt)
    
    
    #davidson
    davidson = 1
    if davidson == 1:
        n0 = H_sectors[0,0].shape[0] 

        c_0 =  np.dot(vp[0:n0,0].T,vp[0:n0,0])
        ltmp, vtmp = np.linalg.eigh(H0_0)
        davidson_correction = (1-c_0)*(lp[0] - ltmp[0])/c_0
        print " Norm of low-entanglement reference component %12.8f" %c_0
        print " Davidson correction :                        %12.8f " %davidson_correction
        #lp[0] += davidson_correction
    
    #pt2
    if args['pt_order'] == 2:
        n0 = H_sectors[0,0].shape[0] 
        Hpp = Htest[0:n0, 0:n0]
        Hpq = Htest[0:n0, n0::]

        Dqq = np.array([])

        if args['pt_type'] == 'en':
            Dqq = np.diag(Htest)[n0::]    #Epstein-Nesbitt-like
        elif args['pt_type'] == 'mp':
            Dqq = H_zero_order_diag[n0::]    #Moller-Plesset-like
        else:
            print " Bad choice of pt_type"
            exit(-1)
        
        H0 = Hpp
        l0,v0 = np.linalg.eigh(H0)
        e0 = l0[0]

        Dqq = 1/(e0-Dqq) 
        H2 = Hpp + Hpq.dot(np.diag(Dqq)).dot(Hpq.T)

        l2,v2 = np.linalg.eigh(H2)
        print " Zeroth-order energy: %12.8f" %l0[0]
        print " Second-order energy: %12.8f" %l2[0]

    print " %5s    %16s  %16s  %12s" %("State","Energy","Relative","<S2>")
    for si,i in enumerate(lp):
        print " %5i =  %16.8f  %16.8f  %12.8f" %(si,i*convert,(i-lp[0])*convert,abs(s2[si,si]))
        if si>args['n_print']:
            break
    
    #print
    #print " Energy  Error due to compression    :  %12.8f - %12.8f = %12.8f" %(lp[0],l[0],lp[0]-l[0])


    energy_per_iter += [lp[target_state]]

    thresh = 1.0*np.power(10.0,-float(args['thresh']))
    if it > 0:
        if abs(lp[target_state]-energy_per_iter[it-1]) < thresh:
            break
            #if diis == 1:
            #    diis = 0
            #else:
            #    break

    #
    #   todo: look for, and address, root flipping
    #
    #check if root flipped
    #if 1:
        #vec_curr.shape = dim_tot
    #    last_vector = cp.deepcopy(vp[:,target_state])


    #
    # Get dimensions of all the spaces
    #
    n0 = H_sectors[0,0].shape[0] 
    
    P_dim = n0
    Q_dims = [] # dimension of Q space for each block i.e., Q_dims[3] is the dimension of this space |abcDef...> 
    QQ_dims = [] # dimension of Q space for each block-dimer i.e., QQ_dims[3] is the dimension of this space |AbcdEf...> 
    QQQ_dims = []

    #   These arrays of pairs indicate where each P,Q,QQ, etc block starts and stops in the compressed CI space
    ci_startstop     = {}

    ci_startstop[-1] = (0,n0)

    start = n0 
    if n_body_order >= 1: 
        print 
        print " Form fragment-reduced density matrices"
        for bi,b in enumerate(blocks):
            #q_dim = n0 / p_states[bi].shape[1] * q_states[bi].shape[1]
            q_dim = H_sectors[bi+1,bi+1].shape[0]
            Q_dims.extend([q_dim])
           
            ci_startstop[bi] = (start,start+q_dim)
 
            start = start + q_dim
 
    if n_body_order >= 2: 
        for bi,b in enumerate(blocks):
            for bbi,bb in enumerate(blocks):
                if bbi > bi:
                    bij = (bi+1, bbi+1)
                    #q_dim = n0 / p_states[bi].shape[1] / p_states[bbi].shape[1] * q_states[bi].shape[1] * q_states[bbi].shape[1]
                    q_dim = H_sectors[bij,bij].shape[0]
                    QQ_dims.extend([q_dim])
                    
                    ci_startstop[(bi,bbi)] = (start,start+q_dim)
            
                    start = start + q_dim
 
 
    if n_body_order >= 3: 
        for bi,b in enumerate(blocks):
            for bbi,bb in enumerate(blocks):
                if bbi > bi:
                    for bbbi,bbb in enumerate(blocks):
                        if bbbi > bbi:
                            q_dim = n0 
                            q_dim = q_dim / p_states[bi].shape[1]   * q_states[bi].shape[1]
                            q_dim = q_dim / p_states[bbi].shape[1]  * q_states[bbi].shape[1]
                            q_dim = q_dim / p_states[bbbi].shape[1] * q_states[bbbi].shape[1]
                            QQQ_dims.extend([q_dim])
                    
                            ci_startstop[(bi,bbi,bbbi)] = (start,start+q_dim)
            
                            start = start + q_dim
    
    print
    print " Dimensions of all the spaces"
    print " P_dims  ", P_dim
    print " Q_dims  ", Q_dims
    print " QQ_dims ", QQ_dims
    print " QQQ_dims", QQQ_dims
    print


    #
    #   
    #   Update Tucker factors
    #
    #

    if it<maxiter-0 :
# {{{
        #
        #   (A a1 a2 a3) (B b1 b2 b3) = AB a1 b1
        v = cp.deepcopy(vp[:,target_state])
        
        v_0 = v[0:P_dim]

        n0 = 1   # this is the size of the PPPP block (before m_s projection)
        for bi,b in enumerate(blocks):
            n0 *= p_states[bi].shape[1]


        # unproject back from m_s subblock
        if ms_proj:
            ms_space_P = get_ms_subspace_list2(vecs0, Szi, Szij, target_ms)
            #ms_space_P = get_ms_subspace_list(vecs0, Szi, target_ms)
            tmp = np.zeros((n0))
            tmp[ms_space_P] = v_0
            v_0 = cp.deepcopy(tmp)


        v_0.shape = n_p_states
        grams = {}
        
        
        #
        # PP terms
        print " P,P block" 
        for fi,f in enumerate(blocks):
            #print " Get gramian for block", fi,
            gram_tmp = form_1fdm(v_0, v_0, [fi])
            #print " size: ", gram_tmp.shape,
            #print " trace: %16.12f"% gram_tmp.trace()
    
            grams[fi] = vecs0[fi].dot(gram_tmp).dot(vecs0[fi].T)

     
        #
        # P,Q terms
        if n_body_order >= 1:
            print
            print " P,Q block" 
            
            for bi,b in enumerate(blocks):
                print " Q = ", bi
                start = ci_startstop[bi][0] 
                stop  = ci_startstop[bi][1] 
                v1 = cp.deepcopy(vp[start:stop,target_state])
          
                # unproject back from m_s subblock
                if ms_proj:
                    ms_space_curr = get_ms_subspace_list2(vecsQ[bi], Szi, Szij, target_ms)
                    #ms_space_curr = get_ms_subspace_list(vecsQ[bi], Szi, target_ms)
                    n_curr = n0 * q_states[bi].shape[1] / p_states[bi].shape[1]
                    tmp = np.zeros((n_curr))
                    tmp[ms_space_curr] = v1
                    v1 = cp.deepcopy(tmp)


                
                dims_curr = cp.deepcopy(n_p_states)
                dims_curr[bi] = q_states[bi].shape[1]
                
                v1.shape = dims_curr
            
                #print "   Get gramian for block: ", bi, 
                gram_tmp = form_1fdm(v_0, v1, [bi])
                #print " size: %5s x %-5s"%(gram_tmp.shape[0],gram_tmp.shape[1]),
                #print " trace: %16.12f"% gram_tmp.trace()
                
                gram_tmp = vecs0[bi].dot(gram_tmp).dot(vecsQ[bi][bi].T)

                grams[bi] += gram_tmp + gram_tmp.T
       
        #
        # Q,Q terms
        if n_body_order >= 1:
            print
            print " Q,Q block" 
            
            
            for bi,b in enumerate(blocks):
                print " Q = ", bi
                start = ci_startstop[bi][0] 
                stop  = ci_startstop[bi][1] 
                v1 = cp.deepcopy(vp[start:stop,target_state])
                #print " Norm of Q: ", np.linalg.norm(v1)
                
                
                # unproject back from m_s subblock
                if ms_proj:
                    ms_space_curr = get_ms_subspace_list2(vecsQ[bi], Szi, Szij, target_ms)
                    #ms_space_curr = get_ms_subspace_list(vecsQ[bi], Szi, target_ms)
                    n_curr = n0 * q_states[bi].shape[1] / p_states[bi].shape[1]
                    tmp = np.zeros((n_curr))
                    tmp[ms_space_curr] = v1
                    v1 = cp.deepcopy(tmp)

                
                dims_curr = cp.deepcopy(n_p_states)
                dims_curr[bi] = q_states[bi].shape[1]
                
                v1.shape = dims_curr
            
                for fi,f in enumerate(blocks):
                    #print "   Get gramian for block: ", fi, 
                    gram_tmp = form_1fdm(v1, v1, [fi])
                    #print " size: %5s x %-5s"%(gram_tmp.shape[0],gram_tmp.shape[1]),
                    #print " trace: %16.12f"% gram_tmp.trace()
                    
                    grams[fi] += vecsQ[bi][fi].dot(gram_tmp).dot(vecsQ[bi][fi].T)
       
        
        #
        # Q,QQ terms 
        if n_body_order >= 2:
            #   These terms will only give a nonzero contribution to the 1fdm when one of the Q blocks coincide
            #
            #      i.e.,  
            #           D2 = |b><B| { <Acd|Acd> + <aCd|aCd> + <acD|acD> }
            #
            print
            print " Q,QQ block" 
            
            start1 = P_dim  #indexing for Q blocks
            start2 = P_dim  #indexing for QQ blocks

            for di,d in enumerate(Q_dims):
                start2 += d
            
            block_dimer_index = 0
            
            for bi,b in enumerate(blocks):
                stop1 = start1 + Q_dims[bi]
                for bbi,bb in enumerate(blocks):
                    if bbi > bi:
                        print " QQ = ", (bi,bbi)
                        
                        start2 = ci_startstop[(bi,bbi)][0] 
                        stop2  = ci_startstop[(bi,bbi)][1] 
                        
                        v2 = cp.deepcopy(vp[start2:stop2,target_state])
              

                        # unproject back from m_s subblock
                        if ms_proj:
                            ms_space_curr = get_ms_subspace_list2(vecsQQ[(bi,bbi)], Szi, Szij, target_ms)
                            #ms_space_curr = get_ms_subspace_list(vecsQQ[(bi,bbi)], Szi, target_ms)
                            n_curr = n0 * q_states[bi].shape[1] * q_states[bbi].shape[1] / p_states[bi].shape[1] / p_states[bbi].shape[1]
                            tmp = np.zeros((n_curr))
                            tmp[ms_space_curr] = v2
                            v2 = cp.deepcopy(tmp)

                        
                        dims_curr2 = cp.deepcopy(n_p_states)
                        dims_curr2[bi]  = q_states[bi].shape[1]
                        dims_curr2[bbi] = q_states[bbi].shape[1]
                        
                        v2.shape = dims_curr2

                        #CASE 1: Q,QQ' (i.e., B,BD) this only has a contribution to dD 1fdm
                        start1 = ci_startstop[bi][0] 
                        stop1  = ci_startstop[bi][1] 
                        
                        v1 = cp.deepcopy(vp[start1:stop1,target_state])
                        
                        # unproject back from m_s subblock
                        if ms_proj:
                            ms_space_curr = get_ms_subspace_list2(vecsQ[bi], Szi, Szij, target_ms)
                            #ms_space_curr = get_ms_subspace_list(vecsQ[bi], Szi, target_ms)
                            n_curr = n0 * q_states[bi].shape[1] / p_states[bi].shape[1] 
                            tmp = np.zeros((n_curr))
                            tmp[ms_space_curr] = v1
                            v1 = cp.deepcopy(tmp)

                        dims_curr1 = cp.deepcopy(n_p_states)
                        dims_curr1[bi]  = q_states[bi].shape[1]
                        v1.shape = dims_curr1
                        
                        #print "   Get gramian for block: ", bbi, 
                        gram_tmp = form_1fdm(v1, v2, [bbi])
                        #print " size: %5s x %-5s"%(gram_tmp.shape[0],gram_tmp.shape[1]),
                        #print " trace: %16.12f"% gram_tmp.trace()
                            
                        gram_tmp = vecsQ[(bi)][bbi].dot(gram_tmp).dot(vecsQQ[(bi,bbi)][bbi].T)

                        grams[bbi] -= gram_tmp + gram_tmp.T      # why is this negative?!!

                        
                        
                        #CASE 2: Q,Q'Q (i.e., B,AB) this only has a contribution to aA 1fdm
                        start1 = ci_startstop[bbi][0] 
                        stop1  = ci_startstop[bbi][1] 
                        
                        v1 = cp.deepcopy(vp[start1:stop1,target_state])
                        
                        # unproject back from m_s subblock
                        if ms_proj:
                            ms_space_curr = get_ms_subspace_list2(vecsQ[bbi], Szi, Szij, target_ms)
                            #ms_space_curr = get_ms_subspace_list(vecsQ[bbi], Szi, target_ms)
                            n_curr = n0 * q_states[bbi].shape[1] / p_states[bbi].shape[1] 
                            tmp = np.zeros((n_curr))
                            tmp[ms_space_curr] = v1
                            v1 = cp.deepcopy(tmp)

                        dims_curr1 = cp.deepcopy(n_p_states)
                        dims_curr1[bbi]  = q_states[bbi].shape[1]
                        v1.shape = dims_curr1
                        
                        #print "   Get gramian for block: ", bi, 
                        gram_tmp = form_1fdm(v1, v2, [bi])
                        #print " size: %5s x %-5s"%(gram_tmp.shape[0],gram_tmp.shape[1]),
                        #print " trace: %16.12f"% gram_tmp.trace()
                            
                        gram_tmp = vecsQ[(bbi)][bi].dot(gram_tmp).dot(vecsQQ[(bi,bbi)][bi].T)


                        grams[bi] -= gram_tmp + gram_tmp.T      # why is this negative?!!
                  
                        block_dimer_index += 1


        #
        # QQ,QQ terms
        #if 0:
        if n_body_order >= 2:
            print
            print " QQ,QQ block" 
            
          
            block_dimer_index = 0
            for bi,b in enumerate(blocks):
                for bbi,bb in enumerate(blocks):
                    if bbi > bi:
                        print " QQ = ", (bi,bbi)
                        start = ci_startstop[(bi,bbi)][0] 
                        stop  = ci_startstop[(bi,bbi)][1] 
                        v1 = cp.deepcopy(vp[start:stop,target_state])

                        # unproject back from m_s subblock
                        if ms_proj:
                            ms_space_curr = get_ms_subspace_list2(vecsQQ[(bi,bbi)], Szi, Szij, target_ms)
                            #ms_space_curr = get_ms_subspace_list(vecsQQ[(bi,bbi)], Szi, target_ms)
                            n_curr = n0 * q_states[bi].shape[1] * q_states[bbi].shape[1] / p_states[bi].shape[1] / p_states[bbi].shape[1]
                            tmp = np.zeros((n_curr))
                            tmp[ms_space_curr] = v1
                            v1 = cp.deepcopy(tmp)

                        
                        dims_curr = cp.deepcopy(n_p_states)
                        dims_curr[bi]  = q_states[bi].shape[1]
                        dims_curr[bbi] = q_states[bbi].shape[1]
                        
                        v1.shape = dims_curr
                     
                        for fi,f in enumerate(blocks):
                            #print "   Get gramian for block: ", fi, 
                            gram_tmp = form_1fdm(v1, v1, [fi])
                            #print " size: %5s x %-5s"%(gram_tmp.shape[0],gram_tmp.shape[1]),
                            #print " trace: %16.12f"% gram_tmp.trace()
                            
                            grams[fi] += vecsQQ[(bi,bbi)][fi].dot(gram_tmp).dot(vecsQQ[(bi,bbi)][fi].T)
                  
                  
                        block_dimer_index += 1
        # }}}
     

        p_states_new = []
        q_states_new = []
        print "    Eigenvalues of each 1fdm:" 
        for fi,f in enumerate(blocks):
            old_basis = np.hstack((p_states[fi], q_states[fi]))
            
            gram_curr = grams[fi] + S2i[fi]
          
            if opt == "diis":
                n_diis_vecs = 8 
                proj_p = p_states[fi].dot(p_states[fi].T)
                error_vector = proj_p.dot(grams[fi] + S2i[fi]) - (grams[fi] + S2i[fi]).dot(proj_p)
                #error_vector = (q_states[fi].T.dot(grams[fi] + S2i[fi]).dot(p_states[fi]) )
                #error_vector = (q_states[fi].T.dot(grams[fi]).dot(p_states[fi]) )
            
                
                diff_err_vec = 0
                if diff_err_vec == 1:
                    if it == 0: 
                        error_vector = grams[fi] + S2i[fi]
                        #error_vector = cp.deepcopy(grams[fi])
                    else:
                        error_vector = grams[fi] + S2i[fi] - diis_frag_grams[fi][0]
                        #error_vector = grams[fi] + S2i[fi] - diis_frag_grams[fi][-1]

               
                error_vector.shape = (error_vector.shape[0]*error_vector.shape[1],1)
           
                print " Dimension of Error Vector matrix: ", diis_err_vecs[fi].shape
                if diis_err_vecs[fi].shape[0] == 0:
                    diis_err_vecs[fi] = error_vector
                else:
                    diis_err_vecs[fi] = np.hstack( (diis_err_vecs[fi], error_vector) ) 


                diis_frag_grams[fi].append( grams[fi] + S2i[fi])
                
                n_evecs = diis_err_vecs[fi].shape[1]


                #if n_evecs == n_diis_vecs:
                #    tmp = np.hstack( (diis_err_vecs[fi][:,1:-1], error_vector) )
                #elif n_evecs < n_diis_vecs:
                #    tmp = np.hstack( (diis_err_vecs[fi], error_vector) )
                #else:
                #    print "wtf?"
                #    exit(-1)
                #only add linearly independant vectors
                #if abs(np.linalg.det(tmp.T.dot(tmp))) > 1e-15:
                #    diis_err_vecs[fi] = tmp 
               
                
                #if n_evecs == n_diis_vecs:
                #    diis_frag_grams[fi].pop(0)
                #    diis_err_vecs[fi].pop(0) 
            
                
                if it>0:
                    

                    S = diis_err_vecs[fi].T.dot(diis_err_vecs[fi] )

                  
                    rm_lin_dep = 0
                    if rm_lin_dep:
                        v = cp.deepcopy(diis_err_vecs[fi])
                        for vi in range(0,v.shape[1]):
                            v[:,vi] = v[:,vi]/np.linalg.norm(v[:,vi])
                        Sv = v.T.dot(v)

                        #lx,vx = np.linalg.eigh(Sv)
                        
                        #sort_ind = np.argsort(abs(lx))
                        #lx = lx[sort_ind]
                        #vx = vx[:,sort_ind]
                        ux,lx,vx = np.linalg.svd(v)

                        to_del = np.zeros((v.shape[1],1),dtype=int) 

                    
                        for i in range(2,lx.shape[0]):
                            print " Singular value of v %18.2e" %lx[i]
                            if abs(lx[i]) < 1e-9:
                                to_del[np.argmax(abs(vx[:,i]))] = 1
                                #for vi in range(0,vx.shape[0]):
                                    #print "Coeff ", vx[vi,i]
                                    #if abs(vx[vi,i]) > 1e-2:
                                    #    to_del[vi] = 1


                        print " Delete: ",to_del 

                        v_new = np.empty(( diis_err_vecs[fi].shape[0],0))
                        G_new = [] 
                        print diis_err_vecs[fi].shape
                        for vi in range(0,v.shape[1]):
                            if to_del[vi] == 0:
                                v_new = np.hstack(( v_new,diis_err_vecs[fi][:,vi:vi+1] ))
                                G_new.append(diis_frag_grams[fi][vi])

                        diis_err_vecs[fi] = cp.deepcopy(v_new)
                        diis_frag_grams[fi] = cp.deepcopy(G_new)
                    
                        S = diis_err_vecs[fi].T.dot(diis_err_vecs[fi] )





                    collapse = 1
                    if collapse:
                        
                       
                        sort_ind = np.argsort(S.diagonal())
                        #sort_ind = np.argsort(lt)[::-1]

                        #sort_ind = [sort_ind[i] for i in sort_ind]
                        sort_ind = [sort_ind[i] for i in range(0,min(len(sort_ind),n_diis_vecs))]
        

                        diis_err_vecs[fi] = diis_err_vecs[fi][:,sort_ind]
                        tmp = []
                        for i in sort_ind:
                            tmp.append(diis_frag_grams[fi][i])
                        diis_frag_grams[fi] = cp.deepcopy(tmp)

                        #diis_frag_grams[fi] = [diis_frag_grams[fi][i] for i in sort_ind]
                        #diis_frag_grams[fi] =diis_frag_grams[fi][sort_ind]  


                        print "Vector errors", S.diagonal()[sort_ind] 
                        
                        #nv = 0
                        #for i in lt:
                        #    if abs(i) > 1e-16:
                        #        nv += 1
                        #if nv==0:
                        #    print "What?"
                        #    exit(-1)
                        #print " Number of linearly independent DIIS vectors: ", nv

#                        vt = vt[:,0:min(nv,n_diis_vecs)]
#
#                        diis_err_vecs[fi] = diis_err_vecs[fi].dot(vt) 
#                        for v in range(0,vt.shape[1]):
#                            print " Eigval: %12.6e" %lt[v]
#                            gram_tmp = np.zeros((grams[fi].shape[0],grams[fi].shape[1]))
#                            for i in range(0,vt.shape[0]):
#                                gram_tmp += diis_frag_grams[fi][v] * vt[i,v]
#                            diis_frag_grams[fi][v] = cp.deepcopy(gram_tmp)
#            
#                        diis_err_vecs[fi] = diis_err_vecs[fi][:,n_evecs-n_diis_vecs:n_evecs]
#                        diis_frag_grams[fi] = diis_frag_grams[fi][-n_diis_vecs:]
                        n_evecs = diis_err_vecs[fi].shape[1]
                        S = diis_err_vecs[fi].T.dot(diis_err_vecs[fi] )
                   

                    print " Number of error vectors: %4i " %n_evecs
                    B = np.ones( (n_evecs+1, n_evecs+1) )
                    B[-1,-1] = 0

                
                    B[0:-1,0:-1] = cp.deepcopy(S) 
                    r = np.zeros( (n_evecs+1,1) )
                    r[-1] = 1
                    if n_evecs > 0: 
                        #x = np.linalg.solve(B, r)
                        x = np.linalg.pinv(B).dot(r)
                        
                        #x = x / np.sum(x)
                        #print " Sum %12.8e"% np.sum(x)
                        #gram_curr = np.zeros(gram_curr.shape)
                        extrap_err_vec = np.zeros((diis_err_vecs[fi].shape[0]))
                        #extrap_err_vec = error_vector 
                        extrap_err_vec.shape = (extrap_err_vec.shape[0])

                        for i in range(0,x.shape[0]-1):
                            gram_curr += x[i]*diis_frag_grams[fi][i]
                            extrap_err_vec += x[i]*diis_err_vecs[fi][:,i]
                        
                        print " DIIS Coeffs"
                        for i in x:
                            print "  %12.8f" %i
                        #print x.T
                        print 
                        print " CURRENT           error vector %12.2e " % error_vector.T.dot(error_vector)
                        #print " DIIS extrapolated error vector %12.2e " % extrap_err_vec.dot(extrap_err_vec)
            

            #error_vector = p_states[fi].T.dot(grams[fi]).dot(p_states[fi])
            #error_vector = p_states[fi].T.dot(grams[fi]+S2i[fi]) - (grams[fi]+S2i[fi]).T.dot(p_states[fi])
               
            #print " Norm of residual vector\n", error_vector.T.dot(error_vector)

            #lx,vx = np.linalg.eigh(old_basis.T.dot(grams[fi]).dot(old_basis))
            #vx = old_basis.dot(vx)
            #lx = vx.T.dot(grams[fi]).dot(vx).diagonal()

            # this makes sure we keep spin states pure. 
            lx,vx = np.linalg.eigh(gram_curr + S2i[fi])

            lx = vx.T.dot(grams[fi]).dot(vx).diagonal()
       
            sort_ind = np.argsort(lx)[::-1]
            lx = lx[sort_ind]
            vx = vx[:,sort_ind]
            
            vp = vx[:,0:n_p_states[fi]]
            vq = vx[:,n_p_states[fi]:n_p_states[fi]+n_q_states[fi]]

            tmp, up = np.linalg.eigh(vp.T.dot(grams[fi] + Hi[fi] + Szi[fi] + S2i[fi]).dot(vp))
            tmp, uq = np.linalg.eigh(vq.T.dot(grams[fi] + Hi[fi] + Szi[fi] + S2i[fi]).dot(vq))
           
            vp = vp.dot(up)
            vq = vq.dot(uq)

            sort_ind = np.argsort(vp.T.dot(grams[fi]).dot(vp).diagonal() )[::-1]
            vp = vp[:,sort_ind]
            sort_ind = np.argsort(vq.T.dot(grams[fi]).dot(vq).diagonal() )[::-1]
            vq = vq[:,sort_ind]
           
            v = np.hstack( ( vp,vq) )
            sz = v.T.dot(Szi[fi]).dot(v).diagonal()
            s2 = v.T.dot(S2i[fi]).dot(v).diagonal()
            lx = v.T.dot(grams[fi]).dot(v).diagonal()
            h = v.T.dot(Hi[fi]).dot(v).diagonal()
           
            print "         Fragment: ", fi
            print "   %-12s   %16s  %16s  %12s  %12s "%("Local State", "Occ. Number", "<H>", "<S2>", "<Sz>")
            for si,i in enumerate(lx):
                print "   %-12i   %16.8f  %16.8f  %12.4f  %12.4f "%(si,lx[si],h[si],abs(s2[si]),sz[si])
                #print "   %-4i   %16.8f  %16.8f  %16.4f "%(si,lx[si],h[si],sz[i])
            print "   %-12s " %("----")
            print "   %-12s   %16.8f  %16.8f  %12.4f  %12.4f" %(
                    "Trace"
                    ,(grams[fi]).trace()
                    ,Hi[fi].dot(grams[fi]).trace()
                    ,S2i[fi].dot(grams[fi]).trace()
                    ,Szi[fi].dot(grams[fi]).trace()
                    )
            print 
            #print lx

            p_states_new.extend([vp])
            q_states_new.extend([vq])

        p_states = p_states_new 
        q_states = q_states_new 








    #if it<maxiter-1 :
    if 0 :
        print " Recompose target state (SLOW)"
   # {{{
        v = cp.deepcopy(vp[:,target_state])
        
        v_0 = v[0:P_dim]
        v_0.shape = n_p_states
   
        vec_curr = transform_tensor(v_0, vecs0)
    
        if n_body_order >= 1:
            
            start = P_dim
            for bi,b in enumerate(blocks):
                print bi
                stop = start + Q_dims[bi]
                v_tmp = cp.deepcopy(vp[start:stop,target_state])
        
                # copy all P space vectors, and replace current block with Q vectors
                vecs_b = cp.deepcopy(vecs0)
                vecs_b[bi] = q_states[bi]
                
                dim_b = cp.deepcopy(n_p_states)
                dim_b[bi] = q_states[bi].shape[1]
                v_tmp = v_tmp.reshape(dim_b)
               
                # add this recomposed portion of the CI vector
                vec_curr += transform_tensor(v_tmp, vecs_b)
                start = stop
        
        if n_body_order >= 2:
            
            block_dimer_index = 0
            for bi,b in enumerate(blocks):
                for bbi,bb in enumerate(blocks):
                    if bbi > bi:

                        stop = start + QQ_dims[block_dimer_index]
                        v_tmp = cp.deepcopy(vp[start:stop,target_state])
                     
                        # copy all P space vectors, and replace current block with Q vectors
                        vecs_b = cp.deepcopy(vecs0)
                        vecs_b[bi] = q_states[bi]
                        vecs_b[bbi] = q_states[bbi]
                        
                        dim_b       = cp.deepcopy(n_p_states)
                        dim_b[bi]   = q_states[bi].shape[1]
                        dim_b[bbi]  = q_states[bbi].shape[1]
                        
                        v_tmp = v_tmp.reshape(dim_b)
                        
                        # add this recomposed portion of the CI vector
                        vec_curr -= transform_tensor(v_tmp, vecs_b)

                        block_dimer_index += 1
                        print "QQ_dims, start, stop", start, stop
                        start = stop
        
        
        Acore, Atfac = tucker_decompose(vec_curr,0,0)
        p_states = []
        q_states = []
        for bi,b in enumerate(Atfac):
            p_states.extend([b[:,0:n_p_states[bi]]])
            q_states.extend([b[:,n_p_states[bi]:n_p_states[bi]+n_q_states[bi]]])
      
        vec_curr = vec_curr.reshape(dim_tot)
        #H_tot = H_tot.reshape(dim_tot, dim_tot)# }}}
        


<<<<<<< HEAD:deprecated/nbody-hbuild.py
=======
    print " %5s    %16s  %16s  %12s" %("State","Energy","Relative","<S2>")
    for si,i in enumerate(lp):
        print " %5i =  %16.8f  %16.8f  %12.8f" %(si,i*convert,(i-lp[0])*convert,abs(s2[si,si]))
        if si>args['n_print']:
            break
    
    #print
    #print " Energy  Error due to compression    :  %12.8f - %12.8f = %12.8f" %(lp[0],l[0],lp[0]-l[0])


    energy_per_iter += [lp[target_state]]

    thresh = 1.0*np.power(10.0,-float(args['thresh']))
    if it > 0:
        if abs(lp[target_state]-energy_per_iter[it-1]) < thresh:
            break# }}}
>>>>>>> master:nbody-hbuild.py

    
    
    
    
    
    
print " %10s  %12s  %12s" %("Iteration", "Energy", "Delta")
for ei,e in enumerate(energy_per_iter):
    if ei>0:
        print " %10i  %12.8f  %12.1e" %(ei,e,e-energy_per_iter[ei-1])
    else:
        print " %10i  %12.8f  %12s" %(ei,e,"")



