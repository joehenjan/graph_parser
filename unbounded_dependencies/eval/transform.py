def transform(t2props_dict, t2topsub_dict, sent_t, parse_t, stag_t=[], pos_t=[],  only_deep_arg=False, add_plus=False, add_predicative = True,
            skip_unseen_words=False, dont_skip_wildcards=False, forbid_vacuous=False, fuzz_wildcards_and_contractions=True, debug=False, debug_subset=False, return_breaking_triple=False, flags={}):
    

    # NOTE: use list() to make a copy, instead of modifying the original parse_t
    parse_t = [(dep[0], dep[1], dep[2].replace('-unk-', 'ADJ')) for dep in parse_t]

    # structural transformations, used in any case

    # method 1: add triples in parallel for predaux, rel, modif:NP. 
    # Extend this output by adding triples for predicative and and_but. 

    to_add = []

    # predicative auxiliary clause, relative clause, modif:NP, 
    # added in parallel
    for triple in parse_t:
        # flipped predicative auxiliary clause
        candidate = add_flipped_predaux(triple, stag_t, t2props_dict)
        if candidate:
            to_add.append(candidate)
            #if len(sent_t)<=20 and len(sent_t)>15:
            #    print(sent_t)
            #    print(candidate)
        # flipped relative clause
        candidate = add_flipped_rel(triple, parse_t, stag_t, t2props_dict, t2topsub_dict, add_plus=add_plus)
        if candidate:
            to_add.append(candidate)
        # flipped modifying auxiliary clause with relation 1
        #candidate = add_flipped_modif(triple, stag_t, t2props_dict)
        if candidate:
            to_add.append(candidate)
            if  debug >= 3:
                print("parse_t to add for modif:NP:")
                print("orig: ", lexicalize([triple], sent_t, pos=pos_t))
                print("candidate", lexicalize([candidate], sent_t, pos=pos_t))
                print()
#    # extend parse_t for predicative cases
#    if add_predicative:
#        to_add = append_small_clause(parse_t, stag_t, sent_t, t2props_dict)
#        parse_t += to_add 
#        if  debug >= 2:
#            print("parse_t extended with predicative:")
#            print(lexicalize(parse_t, sent_t, pos=pos_t))
#            print()
#
   # update parse_t with results
    parse_t += to_add

   # extend parse_t for and_but cases
    parse_t += append_and_but(parse_t, stag_t, sent_t, pos_t, t2props_dict)
    # extend parse_t for predicative cases
    if add_predicative:
        to_add = append_small_clause(parse_t, stag_t, sent_t, t2props_dict)
        #to_add = []
        parse_t += to_add 
        if  debug >= 2:
            print("parse_t extended with predicative:")
            print(lexicalize(parse_t, sent_t, pos=pos_t))
            print()

    ## co-anchor
    parse_t += add_coanchor(parse_t, stag_t)
    parse_t += add_wh_adj(parse_t, pos_t)
    parse_t += add_copula(sent_t, parse_t, pos_t)
    parse_t += add_nonbe(sent_t, parse_t, pos_t)
    parse_t += add_lot_none(parse_t, sent_t, pos_t)
    parse_t += add_may_have(parse_t, pos_t)
    parse_t += add_there_is(parse_t, pos_t)
    #parse_t += add_sure_of(parse_t, stag_t)
    parse_t += add_the_more(parse_t, stag_t)
    return parse_t
#        if  debug >= 2:
#            print("parse_t extended with and_but:")
#            print(lexicalize(parse_t, sent_t, pos=pos_t))
#            print()
#
#	###### end of structural transformations ######
#    
#    lex_parse_h = lexicalize(parse_h, sent_h, 
#                             pos=pos_h, lemmatize_verbs=flags['lemmatize_verbs'], lemmatize_all=flags['lemmatize_all'])
#    if debug:
#        print("lexicalized parse_h: ", lex_parse_h)
#        print()
#
#    lex_parse_t = lexicalize(parse_t, sent_t, 
#                             pos=pos_t, lemmatize_verbs=flags['lemmatize_verbs'], lemmatize_all=flags['lemmatize_all'])    
#    if debug:
#        print("lexicalized parse_t: ", lex_parse_t)
#        print()
#        
#    if only_deep_arg:
#        lex_parse_h = get_deep_arg_triples(lex_parse_h, only_deep_arg)
#
#        if debug:
#            print("keeping only deep args for lex_parse_h: ", lex_parse_h)
#
#    if skip_unseen_words:
#        lex_parse_h = prune_h_triples_not_in_t(lex_parse_h, lex_parse_t,
#                                               accept_wildcards=dont_skip_wildcards)
#        if debug: 
#            print("pruned lex_parse_h: ", lex_parse_h)
#            print()
#
#    if forbid_vacuous:
#        if lex_parse_h == []:
#            #if True:
#            #    print("vacuous H: sent_t, sent_h", sent_t, sent_h, parse_h)
#            if debug:
#                print("vacuous H, False")
#                print("case sentence:", sent_t)
#                print()
#            return(False)
#
#    return _subset_triples(lex_parse_h, lex_parse_t, fuzz_wildcards_and_contractions=fuzz_wildcards_and_contractions, debug=debug_subset, 
                         #return_breaking_triple=return_breaking_triple)




""" see if hypothesis (h) set is a subset of text (t) set, with some additional conditions """



""" deal with predicative auxiliary cases, modifier auxiliary cases, and relative clause cases"""

# if word has property rel, add a connection to parent with rel: relationship. 
def add_flipped_rel(triple, parse_t, stag_t, t2props_dict, t2topsub_dict, add_plus=False):
    id1, id2, dep = triple[0], triple[1], triple[2]
    
    # try for id1
    stag = _get_stag(id1, stag_t)
    if stag is None:
        return(None)
    
    relation = t2props_dict[stag]['rel']
    if _get_stag(id2, stag_t) == 9:## LRB
        ## get parent of id2
        for child_id, par_id, dep_new in parse_t:
            if child_id == id2 and dep_new == 'ADJ':
                return((par_id,id1,relation))
    if relation in ['0','1','2']:
        return((id2,id1,relation))
    elif ((relation == '+') and add_plus and (stag in t2topsub_dict.keys())):
        return((id2,id1,t2topsub_dict[stag]))
    else:
        return(None)

def add_coanchor(parse_t, sent_t):
    new_edges = []
    for dep, stag in zip(parse_t, sent_t):
        if stag == 'tCO':
            coanchor_id = dep[0]
            head_id = dep[1]
            for dep in parse_t:
                if (dep[0] == head_id):
                    new_edges.append((coanchor_id, dep[1], dep[2]))
                if (dep[1] == head_id):
                    new_edges.append((dep[0], coanchor_id, dep[2]))
    return new_edges
    
def add_lot_none(parse_t, sent_t, pos_t):
    new_edges = []
    par_child_dict =  _triples2par_child_dict(parse_t, sent_t)
    for word_idx, dep, word, pos in zip(range(len(parse_t)), parse_t, sent_t, pos_t):
        if lemmatize(word, pos).lower() in ['lot', 'none', 'kind'] and sent_t[word_idx+1].lower() in ['of']:
            ## lots of people were great
            lot_id = dep[0]
            for par_idx, par_rel in par_child_dict[lot_id]['parents_with_dep']:
                for child_idx, child_rel in par_child_dict[lot_id]['children_with_dep']:
                    ## child_idx great
                    for of_child_idx, of_rel in [(of_child_idx, of_rel) for of_child_idx, of_rel in par_child_dict[word_idx+1+1]['children_with_dep'] if of_rel == '1']:
                        ## of_child_idx people
                        new_edges.append((of_child_idx, par_idx, par_rel))
                        new_edges.append((child_idx, of_child_idx, child_rel))
    return new_edges

def add_sure_of(parse_t, stag_t):
    new_edges = []
    par_child_dict =  _triples2par_child_dict(parse_t, stag_t)
    for word_idx in range(len(stag_t)):
        if stag_t[word_idx] == 't976':
            for child_idx, child_rel in par_child_dict[word_idx+1]['children_with_dep']:
                if child_rel == 'ADJ' and stag_t[child_idx-1] == 't1170':
                    for par_idx, par_rel in par_child_dict[word_idx+1]['parents_with_dep']:
                        if par_rel == 'ADJ':
                            new_edges.append((par_idx, child_idx, '1'))
    return new_edges
def add_the_more(parse_t, stag_t):
    new_edges = []
    for word_idx, dep, stag in zip(range(len(parse_t)), parse_t, stag_t):
        if stag == 't1419':
            if stag_t[word_idx+1] == 't1420':
                new_edges.append((parse_t[word_idx+1][0], dep[1], '1'))
    return new_edges

def add_may_have(parse_t, pos_t):
    new_edges = []
    md_ids = []
    par_child_dict =  _triples2par_child_dict(parse_t, pos_t)
    for i, pos in enumerate(pos_t):
        if pos == 'MD':
            md_ids.append(i+1)
    for md_id in md_ids:
        for par_id, par_dep in par_child_dict[md_id]['parents_with_dep']:
            if par_dep == 'ADJ':
                for child_id, child_dep in par_child_dict[par_id]['children_with_dep']:
                    if md_id != child_id:
                        new_edges.append((md_id, child_id, par_dep))
    return new_edges

def add_there_is(parse_t, pos_t):
    ## there is a man
    new_edges = []
    ex_ids = []
    par_child_dict =  _triples2par_child_dict(parse_t, pos_t)
    for i, pos in enumerate(pos_t):
        if pos == 'EX':
            ex_ids.append(i+1)
    for ex_id in ex_ids:
        for par_id, par_dep in par_child_dict[ex_id]['parents_with_dep']:
            if par_dep == '0': ## man
                for child_id, child_dep in par_child_dict[par_id]['children_with_dep']:## is
                    new_edges.append((par_id, child_id, '0'))
    return new_edges
def add_wh_adj(parse_t, pos_t):
    new_edges = []
    for i in range(len(pos_t)):
        pos = pos_t[i]
        if pos in ['WP', 'WRB', 'WDT']:
            head_id = parse_t[i][0]
            for dep in parse_t:
                if (dep[1] == head_id) and (dep[2] == 'ADJ'):
                    adj_id = dep[0]
                    for dep_ in parse_t:
                        if (dep_[0] == head_id):
                            new_edges.append((adj_id, dep_[1], dep_[2]))
    return new_edges

def add_copula(sent_t, parse_t, pos_t):
    dep_nums = {'0', '1', '2', '3'}
    new_edges = []
    for word_idx, word, pos in zip(range(1, len(sent_t)+1), sent_t, pos_t):
        lemma = lemmatize(word, pos)
        if str(lemma) in ['be']:#, 'stay', 'become', 'remain']: ## copula
            copula_idx = word_idx
            par_child_dict =  _triples2par_child_dict(parse_t, sent_t)
            par_exists = False
            child_exists = False
            for child, rel in par_child_dict[copula_idx]['children_with_dep']:
                if rel == '0':
                    new_child = child
                    child_exists = True
                if rel == '1':
                    new_par = child
                    par_exists = True
            if par_exists and child_exists:
                new_edges.append((new_child, new_par, '0'))
                if ('American' in sent_t) and ('conservatism' in sent_t):
                    print(new_edges)
    return new_edges
                    
def add_nonbe(sent_t, parse_t, pos_t):
    new_edges = []
    for word, dep, pos in zip(sent_t, parse_t, pos_t):
        lemma = lemmatize(word, pos).lower()
        if lemma in ['be', 'stay', 'become', 'seem', 'remain']: ## copula in TAG but not in unbounded dependency
            copula_id = dep[0]
            head_id = dep[1]
            for dep in parse_t:
                if (dep[0] == head_id):
                    new_edges.append((copula_id, dep[1], dep[2]))
                if (dep[1] == head_id):
                    new_edges.append((dep[0], copula_id, dep[2]))
    return new_edges

def add_flipped_predaux(triple, stag_t, t2props_dict):
    id1, id2, dep = triple[0], triple[1], triple[2]
    
    # try for id1
    stag = _get_stag(id1, stag_t)
    if stag is None:
        return(None)
    
    elif t2props_dict[stag]['predaux'] == 'TRUE':
        # get deepsubcategory, of the form dsubcat:NP#0_NP#1_NP#2
        # Then get phrase types like NP#0, S#1, etc.
        phrase_types = t2props_dict[stag]['dsubcat'].split('_')
        root = t2props_dict[stag]['root']
        
        # get rightmost node where phrase type matches root
        # get relation 0,1,2,3 etc
        # QUESTION: why rightmost? Or do we want rightmost case? 
        for phrase_type in phrase_types:

            if phrase_type[0] == root:
                relation = phrase_type[-1]
            
            else: 
                relation = '1' # try adding 1 if there is no corresponding pair.
            
        return((id2,id1,relation))
    
    else:
        return(None)
    
    

def append_small_clause(parse_t, stag_t, sent_t, t2props_dict):   
    to_add = []

    # split sent to list and make it 1-based by adding a 'root' token
    if type(sent_t) == str:
        sent_t = sent_t.split()
    if sent_t[0] != 'root':
        sent_t = ['root'] + sent_t

    if type(stag_t) == str:
        stag_t = stag_t.split()
    if stag_t[0] != 'root':
        stag_t = ['root'] + stag_t

    # check if there are any predicative trees in the sentence,
    # and gather their ids in the sentence. 
    t_pred_tree_ids = []
    for tok_id, tree in enumerate(stag_t):
        try:
            stag = int(tree[1:])
            predicative = t2props_dict[stag]['pred']
        except:
            predicative = None
        if predicative == 'TRUE':
            t_pred_tree_ids.append(tok_id)
    

    # if no pred trees, done
    if not t_pred_tree_ids:
        pass

    # If we have a predicative tree
    else:
        # gather a tree-representation of the text
        par_child_dict = _triples2par_child_dict(parse_t, sent_t)

        # for predicative tree
        for pred_tree_id in t_pred_tree_ids:
            # for 0-child of predicative tree,
            # add dependency to parent(s) of predicative tree
            # (there may be multiple parents due to earlier added dependencies
            # for rel, modif:NP, etc.)

            try:
                zero_child_id = [c_id for c_id, dep in
                                 par_child_dict[pred_tree_id]['children_with_dep']
                                 if dep == '0'][0]
            # not sure when this happens. Maybe misparses. 
            # skip when pred_tree doesn't have a 0-child
            except:
                #print("predicative case without zero child, word: \"", sent_t[pred_tree_id], "\"")
                #print("in sentence:", ' '.join(sent_t))
                #print()
                
                continue

            parents_with_dep_num = [(par_id, dep) for par_id, dep in
                                    par_child_dict[pred_tree_id]['parents_with_dep']
                                    if dep in {'0', '1', '2'}]

            for par_id, dep in parents_with_dep_num:
                to_add.append( (zero_child_id, par_id, dep) )

    return(to_add)

    # return to_add
    
#    # else, for each pred_tree, find all its child dependencies, 
#    # and add connect them with child-0 of pred_tree. 
#    else:
#        to_add = []
#        
#        for id1, id2, dep in parse:
#            # found predicative tree
#            if (stag_t[id2-1] in t_pred_trees):
    #
#                to_add = []
#                id2_children = []
#                id2_zero_child = 0
#                
#                # find all child dependencies
#                for id1, id2_l, dep in parse:
#                    if id2_l == id2:
#                        if dep == '0':
#                            id2_zero_child = id1
#                        else:
#                            id2_children.append((id1, id2_l, dep))
#                
#                # add triples for 0 child
#                for id1, _, dep in id2_children:
#                    to_add.append((id1, id2_zero_child, dep))
                
                
def append_and_but(parse_t, stag_t, sent_t, pos_t, t2props_dict):   
    to_add = []

    modals = ['could', 'should', 'would']
    negations = ["not", "n't"]

    share_partner_parent_modif = ['S', 'NP', 'VP', 'N', 'V', 'MD']
    share_partner_arg_modif = ['VP', 'V', 'S', 'N', 'NP', 'MD'] 

    if type(sent_t) == str:
        sent_t = sent_t.split()
    if sent_t[0] != 'root':
        sent_t = ['root'] + sent_t

    if type(stag_t) == str:
        stag_t = stag_t.split()
    if stag_t[0] != 'root':
        stag_t = ['root'] + stag_t

    if type(pos_t) == str:
        pos_t = pos_t.split()
    if pos_t[0] != 'root':
        pos_t = ['root'] + pos_t
    # for each and_but_tree find 1_child_of_and_but. Find parent_of_and_but. For all relations
    # of parent_of_and_but (or just for 0-relation), add the triple
    # (depnum_child_of_and_butparent, 1_child_of_and_but, depnum)
    and_but_ids = [i for i, w in enumerate(sent_t) if w in ['and', 'but', 'or', ',', '--']]

    if and_but_ids:

        # get tree form
        par_child_dict =  _triples2par_child_dict(parse_t, sent_t)

        # for each 'and' and 'but'
        for and_but_id in and_but_ids:
            stag_tree = stag_t[and_but_id]
            stag = int(stag_tree[1:])
            modif = t2props_dict[stag]['modif']

            if modif in share_partner_parent_modif:
                to_add += _get_partner_parent_rel( sent_t, and_but_id, par_child_dict)
                par_child_dict =  _triples2par_child_dict(parse_t+to_add, sent_t)
            if modif in share_partner_arg_modif:
                rel_case = False
                if modif == 'S':
                    for parent_idx, dep in par_child_dict[and_but_id]['parents_with_dep']:
                        stag_tree = stag_t[parent_idx]
                        if t2props_dict[int(stag_tree[1:])]['rel'] in ['0', '1', '2', '3']:
                            rel_case = True
                to_add += _get_partner_arg_rels( sent_t, pos_t, stag_t, and_but_id, par_child_dict, modals, negations, rel_case, t2props_dict)
                par_child_dict =  _triples2par_child_dict(parse_t+to_add, sent_t)
            to_add += _get_adj_coordination( sent_t, pos_t, stag_t, and_but_id, par_child_dict)
            par_child_dict =  _triples2par_child_dict(parse_t+to_add, sent_t)

    return(to_add)




def _get_partner_parent_rel( sent_t, and_word_id, par_child_dict ):
    to_add = []
    dep_nums = {'0', '1', '2', 'ADJ'}

    # Consider phrase "I think John screamed and ran away"
    # let ran and screamed be "partners". 
    # for relation (screamed, screamed_parent, dep) # if dep in dep_nums, add (ran, screamed_parent, dep)

    # all naming here is relative to 'and'
    # 'and' could also be 'but'
    
    try:
        child_1_id = [c_id for c_id, dep in par_child_dict[and_word_id]['children_with_dep']
                      if dep == '1'][0]
    except:
        # misparsed sentence, where 'and' has no child
        return([])


    # in iterations, may have multiple parents
    # get 'and' parent, e.g. 'screamed'
    for par_id, dep in par_child_dict[and_word_id]['parents_with_dep']:
        
        # get 'screamed' parent, e.g. 'think'
        for partner_par_id, partner_dep in par_child_dict[par_id]['parents_with_dep']:
       
            # if screamed-think dependency is in dep_nums, add that dependency
            # between 'ran' and 'think'
            if partner_dep in dep_nums:

                to_add.append( (child_1_id, partner_par_id, partner_dep) )

    return(to_add)


def _get_adj_coordination( sent_t, pos_t, stag_t, and_word_id, par_child_dict):
    ## a moral, rather than a medical, problem
    new_edges = []
    if stag_t[and_word_id] != 't776':
        return new_edges
    else:
        for par_id, par_dep in par_child_dict[and_word_id]['parents_with_dep']:
            if par_dep == 'ADJ':
                ## par_id: problem
                for child_id, child_dep in par_child_dict[and_word_id]['children_with_dep']:
                    ## child_id: medical
                    new_edges.append((child_id, par_id, 'ADJ'))
    return new_edges
            
    
def _get_partner_arg_rels( sent_t, pos_t, stag_t, and_word_id, par_child_dict, modals, negations, rel_case, t2props_dict):

    to_add = []

    dep_nums = {'0', '1', '2', '3'}
    #print(par_child_dict[and_word_id]['children_with_dep'])

    child_1_ids = [c_id for c_id, dep in par_child_dict[and_word_id]['children_with_dep']
                  if dep == '1']
    if len(child_1_ids) == 0:
        child_1_ids = [c_id for c_id, dep in par_child_dict[and_word_id]['children_with_dep']
                  if dep == 'ADJ']
    if len(child_1_ids) == 0:
        return []
    for child_1_id in child_1_ids:

        add_modals_negations = True
        # if child 1 has modals or negations, 
        # don't add modals or negations from parent
        for grand_child_id, dep in par_child_dict[child_1_id]['children_with_dep']:

            # check if child_1 already has modals or negations
            if ((sent_t[grand_child_id] in modals) or
                (sent_t[grand_child_id] in negations)):
                add_modals_negations = False
            
            # if child_1 already has a dep_num, don't add that dep_num. 
            dep_nums.discard(dep)


        # get parent_id(s) of 'and'
        for par_id, _ in par_child_dict[and_word_id]['parents_with_dep']:

            # go through children of partner
            for partner_child_id, partner_child_dep in par_child_dict[par_id]['children_with_dep']:
                # add if dependency is a numbered dependency
                if partner_child_dep in ['0', '1', '2', '3']:
                        
                    new_dep = partner_child_dep
                    if rel_case:
                        for child_idx, child_dep in par_child_dict[child_1_id]['children_with_dep']:
                            if pos_t[child_idx] in ['WDT', 'WP']:
                                new_dep = child_dep
                    to_add.append( (partner_child_id, child_1_id, new_dep) )
                    rfronts = t2props_dict[int(stag_t[child_1_id][1:])]['rfronts']
                    if 'S#s#1' in rfronts:
                        ## cascade
                        for cascading_par, cascading_dep in par_child_dict[child_1_id]['children_with_dep']:
                            to_add.append((partner_child_id, cascading_par, partner_child_dep))
                # add if word is modal or negation and child_1 has none of those
                elif partner_child_dep == 'ADJ':
                    if partner_child_id > and_word_id:
                        to_add.append( (partner_child_id, child_1_id, partner_child_dep) )
                    
                elif (add_modals_negations and
                    ((sent_t[partner_child_id] in modals) or (sent_t[partner_child_id] in negations))
                   ):
                    to_add.append( (partner_child_id, child_1_id, partner_child_dep) )

                else:
                    pass

    return(to_add)


def _get_relative_case( sent_t, and_word_id, par_child_dict ):
    to_add = []
    dep_nums = {'0', '1', '2'}

    try:
        child_1_id = [c_id for c_id, dep in par_child_dict[and_word_id]['children_with_dep']
                      if dep == '1'][0]
    except:
        # misparsed sentence, where 'and' has no child
        return([])


    # in iterations, may have multiple parents
    # get 'and' parent, e.g. 'screamed'
    for par_id, dep in par_child_dict[and_word_id]['parents_with_dep']:
        
        for partner_par_id, partner_dep in par_child_dict[par_id]['parents_with_dep']:
       
            # if screamed-think dependency is in dep_nums, add that dependency
            # between 'ran' and 'think'
            if partner_dep in dep_nums:

                to_add.append( (child_1_id, partner_par_id, partner_dep) )

    return(to_add)


def _get_stag(tok_id, stag):
    try:
        stag = int(stag[tok_id-1][1:])
        return(stag)
    except:
        return(None)

    

"""
Other entailment_tool functions
"""



"""remove triples in h with tokens that don't appear in t"""

#def prune_h_triples_not_in_t(lex_parse_h, lex_parse_t, accept_wildcards=False):
#
#    words_t = {w1 for w1, _, _ in lex_parse_t}.union({w2 for _, w2, _ in
#                                                     lex_parse_t})
#
#    if accept_wildcards:
#        words_t.union({'somebody', 'someone', 'something'})
#
#    lex_parse_h = list([(w1,w2,dep) for w1,w2,dep in lex_parse_h
#                   if ((w1 in words_t) and (w2 in words_t))])
#
#    return(lex_parse_h)
#
   # sent_t = sent_t.split()
   # 
   # new_lex_parse_h = []
   # 
   # for w1,w2,dep in lex_parse_h:
   #     if ((w1 not in sent_t) or 
   #         (w2 not in sent_t)):
   #         continue
   #     else:
   #         new_lex_parse_h.append((w1,w2,dep))
   # return(new_lex_parse_h)


""" remove triples in h with dependencies other than deep arguments. 
    if only_deep_arg == 1, accept args 0, 1, 2 and 3.
    If only_deep_arg == 2, accept args 0 and 1. """
def get_deep_arg_triples(lex_parse_h, only_deep_arg):

    if only_deep_arg == 1:
        accepted_deps = ['0', '1', '2', '3']
    elif only_deep_arg == 2:
        accepted_deps = ['0', '1']
    else:
        ValueError("flag only_deep_arg should be 0, 1, or 2")

    lex_parse_h = list([(w1,w2,dep) for w1,w2,dep in lex_parse_h
                   if (dep in accepted_deps)])

    return(lex_parse_h)


""" lemmatizer """
def get_wordnet_pos(treebank_tag):
    from nltk.corpus import wordnet

    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    # default to noun
    else:
        return wordnet.NOUN

def lemmatize(word, pos):
    from nltk.stem import WordNetLemmatizer

    lemma = WordNetLemmatizer().lemmatize
    
    pos = get_wordnet_pos(pos)
    
    return(lemma(word, pos))



# for a sentence, take its parse with integer ids and 
# replace the integers with lexicalizations
def lexicalize(parse, text, stag= [], pos=[], lemmatize_verbs=False, lemmatize_all=False):   
    # convert text from string to list
    if type(text) == type(""):
        text = text.split()
    # add "root"
    text = ['root'] + text
    if pos != []:
        if type(pos) == str:
            pos = pos.split()
        pos = ['root'] + pos
    # lexicalize
    lex_parse = []    
    for id1, id2, dep in parse:
        word1 = text[id1].lower()
        word2 = text[id2].lower()
        if stag != []:
            word1 +=  " " + stag[id1]
            word2 +=  " " + stag[id2]
        if lemmatize_all:
            word1 = lemmatize(word1, pos[id1])
            word2 = lemmatize(word2, pos[id2])
        elif lemmatize_verbs:
            word1_pos = pos[id1]
            word2_pos = pos[id2]
            # if word1 is a verb, lemmatize it
            if word1_pos.startswith('V'):
                word1 = lemmatize(word1, pos[id1])
            # if word2 is a verb, lemmatize it
            if word2_pos.startswith('V'):
                word2 = lemmatize(word2, pos[id2])            
        lex_parse.append((word1, word2, dep))
    return(lex_parse)



def _triples2par_child_dict(parse_t, sent_t):
    from collections import defaultdict
    par_child_dict = defaultdict(lambda: defaultdict(list))

    for id1, id2, dep in parse_t:
        par_child_dict[id1]['parents_with_dep'].append( (id2, dep) )
        par_child_dict[id2]['children_with_dep'].append( (id1, dep) )

    return(par_child_dict)
if __name__ == '__main__':
    print(lemmatize('stayed', 'V'))
    print(lemmatize('which', 'V'))
    print(lemmatize('what', 'V'))
    print(lemmatize('None', 'V'))
    print(lemmatize('lots', 'V'))
    from get_treeprops import get_t2props_dict, get_t2topsub_dict
    tree_prop_file = 'd6.treeproperties'
    t2props_dict = get_t2props_dict(tree_prop_file)
    t2topsub_dict = get_t2topsub_dict(tree_prop_file)
    stag = 3339 
    print('S#s#1' in t2props_dict[stag]['rfronts'])
