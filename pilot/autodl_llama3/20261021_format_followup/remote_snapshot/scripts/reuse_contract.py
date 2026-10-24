def reusable(old,current):
    # Position, source row, all relevant dynamic label state, partially-built row,
    # exact serialized prompt, and every actual generation parameter must match.
    return old['context']==current['context'] and old['request']==current['request']
