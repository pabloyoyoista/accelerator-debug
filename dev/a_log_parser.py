datasets = ('source', 'previous')


def prepare(job):
    dw = job.datasetwriter(caption='parsed', previous=datasets.previous)
    dw.add('time', 'parsed:int64')
    dw.add('value', 'parsed:int32')
    return dw


def analysis(sliceno, prepare_res):
    dw = prepare_res
    cols = 'data'
    for data in datasets.source.iterate(sliceno, cols):
        data = data.decode("utf-8").strip().split(',')
        dw.write_list(data)
