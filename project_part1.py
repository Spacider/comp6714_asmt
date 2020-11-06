
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


def delete_smallest(Ans):
    # Ans (score, docID)
    min_result = Ans[0]
    for result in Ans:
        if result[0] <= min_result[0]:
            min_result = result
    Ans.remove(min_result)
    return Ans


def smallest_threshold(Ans):

    min_threshold = Ans[0][0]

    for item in Ans:
        if item[0] < min_threshold:
            min_threshold = item[0]

    return min_threshold


def docID(posting):
    return posting[0]


def score(posting):
    return posting[1]


def get_term(candidate_set, pivot):
    return candidate_set[pivot][0]


def get_posting(candidate_set, pivot):
    return candidate_set[pivot][1]


def find_posting_from_term(new_inverted_index, candidates_term):
    for index in new_inverted_index:
        if index[0] == candidates_term:
            return index[1]


# if success, choose new candidates_set(choose all pivot version to next)
def next(candidates_set, new_inverted_index, c_pivot):
    # candidates_set [('Microsoft', (3, 6)) , ('will', (4, 3)), ('Search', (10, 4))]
    # new_inverted_index :
    # [('Microsoft', [(3, 6), (7, 6), (15, 3), (20, 6)]),
    # ('will', [(4, 3), (12, 3), (13, 3), (15, 3), (18, 3)]), ('Search', [(10, 4)])]
    pop_list = []

    for t in range(len(candidates_set)):
        # [('will', (12, 3)), ('Microsoft', (15, 3))]
        candidates_term = get_term(candidates_set, t)
        candidate_posting = get_posting(candidates_set, t)
        if docID(candidate_posting) == c_pivot:
            # need update
            new_posting_list = find_posting_from_term(new_inverted_index, candidates_term)
            for postings_index in range(len(new_posting_list)):
                # if docID equal to cpivot, then need to update
                if docID(new_posting_list[postings_index]) == docID(candidate_posting):
                    # decide whether reach end
                    if postings_index != len(new_posting_list) - 1:
                        # not reach end
                        candidates_set[t] = (candidates_term, new_posting_list[postings_index + 1])
                    else:
                        # reach end
                        pop_list.append(t)
                    break

    for index in reversed(pop_list):
        candidates_set.pop(index)
    return candidates_set


# find next candidate that is larger or equal to cpivot
def seek_to_document(candidates_set, index, new_inverted_index, c_pivot):

    candidates_term = get_term(candidates_set, index)
    candidate_posting = get_posting(candidates_set, index)
    new_posting_list = find_posting_from_term(new_inverted_index, candidates_term)

    for new_index in range(len(new_posting_list)):
        if docID(candidate_posting) == docID(new_posting_list[new_index]):
            while docID(candidate_posting) < c_pivot:
                new_index += 1
                if new_index != len(new_posting_list):
                    # ensure docID larger or equal to c_pivot
                    candidate_posting = new_posting_list[new_index]
                    candidates_set[index] = (get_term(candidates_set, index), candidate_posting)
                else:
                    # if reach end
                    candidates_set.pop(index)
                break
            break

    return candidates_set


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
            new_top_result.extend(sorted(values, key=lambda x: x[1]))

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
    new_inverted_index = list(get_new_inverted_index(query_terms, inverted_index).items())
    # print(new_inverted_index)

    # initiation
    U = {}
    candidates_set = {}
    for t in range(0, len(new_inverted_index)):
        # precompute for maximum weight associated with every t, and store in U
        single_posting_list = get_posting(new_inverted_index, t)
        term = get_term(new_inverted_index, t)
        U[term] = compute_max_score(single_posting_list)
        # add the first posting as candidates
        candidates_set[term] = single_posting_list[0]

    threshold = -1  # current threshold initiate to -1
    Ans = []  # key set of (d, Sd) values
    # candidates_set {'Microsoft': (3, 6), 'will': (4, 3), 'Search': (10, 4)}
    candidates_set = list(dict(sorted(candidates_set.items(), key=lambda x: (x[1][0]))).items())

    # Finding the pivot
    while len(candidates_set) != 0:

        candidates_set = sorted(candidates_set, key=lambda x: (x[1][0]))

        need_full_score = False

        score_limit = 0
        pivot = 0

        while pivot < len(candidates_set):
            pivot_term = get_term(new_inverted_index, pivot)
            temp_s_lim = score_limit + U.get(pivot_term)

            if temp_s_lim > threshold:  # if larger than threshold
                need_full_score = True
                break
            score_limit = temp_s_lim
            pivot += 1

        if not need_full_score:
            pivot = pivot - 1

        c_0 = docID(get_posting(candidates_set, 0))
        c_pivot = docID(get_posting(candidates_set, pivot))

        if need_full_score:
            if c_0 == c_pivot:

                full_evaluation_set.add(c_pivot)
                # print(full_evaluation_set)

                s = 0  # score document c_pivot
                t = 0
                while t < len(candidates_set):
                    # compute full score
                    current_posting = get_posting(candidates_set, t)
                    ct = docID(current_posting)
                    if ct == c_pivot:
                        s += score(current_posting)  # add contribution to score
                    t += 1

                if s > threshold:
                    Ans.append((s, c_pivot))
                    if len(Ans) > top_k:
                        Ans = delete_smallest(Ans)
                        threshold = smallest_threshold(Ans)

                # choose new candidates_set
                candidates_set = next(candidates_set, new_inverted_index, c_pivot)

            else:
                # all smaller than pivot need to be updated!
                for index in range(pivot):
                    candidates_set = seek_to_document(candidates_set, index, new_inverted_index, c_pivot)

        else:
            candidates_set = next(candidates_set, new_inverted_index, c_pivot)

    topk_result = sorted(Ans, reverse=True, key=lambda x: x[0])
    topk_result = sorting_same_score(topk_result)
    full_evaluation_count = len(full_evaluation_set)

    return topk_result, full_evaluation_count
