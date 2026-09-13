"""Ranked finite candidates, with explicit bounds and no relationship acceptance."""
import math
import re

from review_ledger_context import require

MAX_SAFE = 2**53-1
LIMIT = ("Finite candidates only. Preserve the whole bound ledger, source identities and original "
         "relationships. Roles, groups, conditions and higher-order meaning stay in their reviewed "
         "relationship records. No candidate is evidence, permission, applicability or acceptance. "
         "Work slots bound declared pool/result work, not integer arithmetic cost or operating-system "
         "time/memory. Large offsets are ranked directly without rescanning earlier results.")


def page_range(request, total, budget, base, per_item):
    offset, limit = request['offset'], request['limit']
    require(isinstance(offset, str) and re.fullmatch(r'0|[1-9][0-9]*', offset), 'offset must be canonical decimal text')
    require(type(limit) is int and 0 < limit <= MAX_SAFE, 'limit must be a positive safe integer')
    require(type(budget) is int and 0 < budget <= MAX_SAFE, 'budget must be a positive safe integer')
    start = int(offset)
    count = min(limit, max(0, total-start))
    slots = base+count*per_item
    require(slots <= budget, 'candidate page exceeds explicit work budget')
    stop = start+count
    return range(start, stop), dict(total=str(total), offset=offset, page_limit=limit,
        next_offset=str(stop) if stop < total else None, work_slots=slots, budget=budget)


def combination_choice(n, remaining, start, rank):
    for choice in range(start, n):
        block = math.comb(n-choice-1, remaining-1)
        if rank < block:
            return choice, rank
        rank -= block
    return None, rank


def combination_at(n, size, rank):
    chosen, start = [], 0
    for remaining in range(size, 0, -1):
        choice, rank = combination_choice(n, remaining, start, rank)
        if choice is not None:
            chosen.append(choice)
            start = choice+1
    return chosen


def arrangement_at(members, size, ordered, repeats, rank):
    if not ordered:
        n = len(members)+size-1 if repeats else len(members)
        choices = combination_at(n, size, rank)
        return [members[choice-position if repeats else choice] for position, choice in enumerate(choices)]
    pool, result = list(members), []
    for remaining in range(size, 0, -1):
        block = len(pool)**(remaining-1) if repeats else math.perm(len(pool)-1, remaining-1)
        number, rank = divmod(rank, block)
        result.append(pool[number] if repeats else pool.pop(number))
    return result


def selection_plan(index, selection):
    require(isinstance(selection, dict) and set(selection)=={'members','size','order','repeats','budget'}, 'invalid selection fields')
    members, size, budget = selection['members'], selection['size'], selection['budget']
    require(isinstance(members, list) and all(isinstance(item, str) and item in index for item in members)
            and len(members)==len(set(members)), 'selection needs unique known member IDs')
    require(type(size) is int and 0 <= size <= MAX_SAFE, 'size must be a nonnegative safe integer')
    require(type(budget) is int and 0 < budget <= MAX_SAFE and len(members)+size <= budget, 'selection exceeds pool budget')
    require(selection['order'] in {'ordered','unordered'} and type(selection['repeats']) is bool, 'invalid selection semantics')
    ordered, repeats = selection['order']=='ordered', selection['repeats']
    members = list(members) if ordered else sorted(members)
    n = len(members)
    if ordered:
        total = n**size if repeats else math.perm(n, size)
    else:
        total = (math.comb(n+size-1,size) if n else int(size==0)) if repeats else math.comb(n,size)
    return members, size, ordered, repeats, total


def selections(data, index, request):
    selection = request['selection']
    members, size, ordered, repeats, total = selection_plan(index, selection)
    ranks, page = page_range(request, total, selection['budget'], len(members)+size, max(1,size*(len(members)+1)))
    items = [dict(index=str(rank), members=arrangement_at(members,size,ordered,repeats,rank),
                  state='unreviewed-candidate') for rank in ranks]
    return {**page, 'selection':{**selection,'members':members}, 'items':items,
            'source_sha256':data['source']['sha256'], 'execution_acceptance':'pending',
            'comparator':'Input position for ordered pools; Unicode code-point ID order for unordered membership.',
            'limit':LIMIT}


def pairs(data, index, request):
    scope = request['scope']
    require(scope in {'all','rules'}, 'unknown candidate scope')
    members = set(index) if scope=='all' else {
        selector for row in data.get('source_records', []) if row.get('kind')=='obligation'
        for selector in ['source:'+row['id']]+['clause:'+part['id'] for part in row.get('clauses', [])]}
    members = sorted(members)
    require(all(member in index for member in members), 'unknown candidate member')
    ranks, page = page_range(request, len(members)**2, request['budget'], len(members), 2)
    items = [dict(index=str(rank), **{'from':members[rank//len(members)], 'to':members[rank%len(members)]},
                  state='unreviewed-candidate') for rank in ranks]
    return {**page, 'scope':scope, 'node_count':len(members), 'items':items,
            'relation_type_candidates':list(data['semantic_model']['relationship_types']),
            'source_sha256':data['source']['sha256'], 'execution_acceptance':'pending',
            'comparator':'Unicode code-point subject ID order; ordered pairs include self-pairs.',
            'limit':LIMIT+' Rules scope selects recorded obligation rows and their clauses; all scope includes every indexed subject.'}
