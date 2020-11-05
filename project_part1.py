
def get_new_inverted_index(query_terms, inverted_index):
    new_inverted_index = dict()
    for key, value in inverted_index.items():
        if key in query_terms:
            new_inverted_index[key] = value

    return new_inverted_index


def compute_max_score(inverted_index):
    max_score = -1
    for index in inverted_index:
        max_score = max(max_score, index[1])
    return max_score


def first_posting(inverted_index_list):
    return inverted_index_list[0]


def delete_smallest(Ans):
    # Ans (score, docID)
    min_result = Ans[0]
    for result in Ans:
        if result[0] <= min_result[0]:
            min_result = result
    Ans.remove(min_result)
    return Ans, min_result[1]


# find next candidate that is larger or equal to cpivot
def seek_to_document(candidates_set, candidate, cmin, whole_inverted_index_list, c_pivot):
    candidates_set.pop(cmin)

    for index in range(len(whole_inverted_index_list[cmin])):
        if docID(whole_inverted_index_list[cmin][index]) == docID(candidate):
            new_candidate = whole_inverted_index_list[cmin][index]
            while docID(new_candidate) < c_pivot:
                index += 1
                if index != len(whole_inverted_index_list[cmin]):
                    # ensure docID larger or equal to c_pivot
                    new_candidate = whole_inverted_index_list[cmin][index]
                    candidates_set.insert(cmin, new_candidate)
                    break
                else:
                    whole_inverted_index_list.pop(cmin)
                    break

    return whole_inverted_index_list, candidates_set


def docID(posting):
    return posting[0]


def score(posting):
    return posting[1]


# if success, choose new candidates_set(choose all pivot version to next)
def next(candidates_set, whole_inverted_index_list, c_pivot):
    # candidates_set [(1, 3), (1, 4), (1, 4)]
    new_candidate_set = []
    new_whole_inverted_index_list = []
    for t in range(len(candidates_set)):
        if docID(candidates_set[t]) == c_pivot:
            for postings_index in range(len(whole_inverted_index_list[t])):
                # if docID equal to cpivot, then need to update
                if docID(whole_inverted_index_list[t][postings_index]) == docID(candidates_set[t]):
                    # decide whether reach end
                    if postings_index != len(whole_inverted_index_list[t]) - 1:
                        # if not reach end, update
                        # decide thether reach end
                        if postings_index != len(whole_inverted_index_list[t]):
                            new_candidate_set.append(whole_inverted_index_list[t][postings_index + 1])
                            new_whole_inverted_index_list.append(whole_inverted_index_list[t])
                        break
        else:
            new_candidate_set.append(candidates_set[t])
            new_whole_inverted_index_list.append(whole_inverted_index_list[t])

    return new_whole_inverted_index_list, new_candidate_set

def sorting_same_score(topk_result):
    # if have same score swap
    dict = {}
    for index in topk_result:
        dict.setdefault(docID(index), []).append(index)

    new_top_result = []
    for key in dict.keys():
        values = dict.get(key)
        if len(values) == 1:
            new_top_result.extend(values)
        elif len(values) > 1:
            new_top_result.extend(          sorted(values, key=lambda x: x[1]))

    return new_top_result


def WAND_Algo(query_terms, top_k, inverted_index):
    # initiate various to return
    # list of (score, doc_id)
    topk_result = []
    #  the number of documents fully evaluated in WAND algorithm.
    full_evaluation_set = set()

    # get the corresponding inverted_index from query terms
    # index      0                    1                                2
    #       {'President': [(1, 2)], 'New': [(1, 2), (2, 1), (3, 1)], 'York': [(1, 2), (2, 1), (3, 1)]}
    # U          2                    2                                2
    new_inverted_index = get_new_inverted_index(query_terms, inverted_index)
    # print(new_inverted_index)


    # initiation
    U = {}
    candidates_set = []
    whole_inverted_index_list = []
    for t in range(0, len(new_inverted_index)):
        # precompute for maximum weight associated with every t, and store in U
        inverted_index_list = list(new_inverted_index.items())[t][1]
        # whole_inverted_index_list stores all inverted_list [[(1, 2)], [(1, 2), (2, 1), (3, 1)], [(1, 2), (2, 1), (3, 1)]]
        whole_inverted_index_list.append(inverted_index_list)

        term = list(new_inverted_index.items())[t][0]
        U[term] = compute_max_score(inverted_index_list)

        # add the first posting as candidates
        posting = first_posting(inverted_index_list)
        candidates_set.append(posting)

    print(U)
    # candidates_set [(1, 3), (1, 4), (1, 4)]

    threshold = -1  # current threshold initiate to -1
    Ans = []  # key set of (d, Sd) values

    # Finding the pivot
    while len(candidates_set) != 0:
        score_limit = 0
        pivot = 0
        while pivot < len(candidates_set) - 1:
            term = list(new_inverted_index.items())[pivot][0]
            print(term)
            temp_s_lim = score_limit + U.get(term)

            if temp_s_lim > threshold:  # if larger than threshold, then will go to line 78
                break
            score_limit = temp_s_lim
            pivot += 1
        # compute c0 as first element
        min_posting = candidates_set[0]
        for c_index in range(1, len(candidates_set)):
            if docID(candidates_set[c_index]) < docID(min_posting):
                min_posting = candidates_set[c_index]

        c_0 = docID(min_posting)
        c_pivot = docID(candidates_set[pivot])
        if c_0 == c_pivot:

            s = 0  # score document c_pivot
            t = 0
            while t < len(candidates_set):
                # compute full score
                ct = docID(candidates_set[t])
                if ct == c_pivot:
                    s += score(candidates_set[t])  # add contribution to score
                t += 1

            full_evaluation_set.add(c_pivot)
            print(full_evaluation_set)
            if s > threshold:
                Ans.append((s, c_pivot))
                if len(Ans) > top_k:
                    Ans, new_threshold = delete_smallest(Ans)
                    threshold = new_threshold
            # choose new candidates_set
            whole_inverted_index_list, candidates_set = next(candidates_set, whole_inverted_index_list, c_pivot)

        else:
            # all smaller than pivot need to be updated!
            for index in range(0, len(candidates_set)):
                if docID(candidates_set[index]) < c_pivot:
                    candidate = candidates_set[index]
                    whole_inverted_index_list, candidates_set = seek_to_document(candidates_set, candidate, index, whole_inverted_index_list, c_pivot)

    topk_result = sorted(Ans, reverse=True, key=lambda x: x[0])
    topk_result = sorting_same_score(topk_result)
    # todo 判定 需要多少次
    # todo the number of documents fully evaluated in WAND algorithm.
    print(full_evaluation_set)
    full_evaluation_count = len(full_evaluation_set)

    return topk_result, full_evaluation_count
