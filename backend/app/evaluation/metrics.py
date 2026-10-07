def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else 0
    r = tp / (tp + fn) if tp + fn else 0
    f = 2 * p * r / (p + r) if p + r else 0
    return p, r, f


def evaluate(gold, pred):
    keys = set(gold) | set(pred)
    tp = sum(gold.get(k) == pred.get(k) and gold.get(k) is not None for k in keys)
    fp = sum(k in pred and pred.get(k) != gold.get(k) for k in keys)
    fn = sum(k in gold and gold.get(k) != pred.get(k) for k in keys)
    p, r, f = prf(tp, fp, fn)
    return {'field_precision': p, 'field_recall': r, 'field_f1': f, 'exact_match': gold == pred}
