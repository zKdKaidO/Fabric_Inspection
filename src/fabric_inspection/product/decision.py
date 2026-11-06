"""Frozen numerical policy is separate from anomaly scoring."""
import math

def decide(score,policy):
    if not math.isfinite(score):raise ValueError('Cannot decide a nonfinite score')
    if score>=policy['hold']:return 'HOLD'
    if score>=policy['review']:return 'REVIEW'
    return 'PASS'
