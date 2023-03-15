import glob
from os.path import basename, join
from accelerator.colour import bold

def main(urd):
    fns = sorted(glob.glob(join(urd.info.input_directory, "*.csv")))
    job_prev = None

    for fn in fns:
        base_fn = basename(fn)
        print(base_fn)
        job_import_log = urd.build(
            'csvimport',
            filename=fn,
            comment='#',
            labelsonfirstline=False,
            labels=['data'],
            separator=';', # This is on purpose, the imports gives a single col
            previous=job_prev,
        )
        job_parse_log = urd.build(
            'log_parser', source=job_import_log, previous=job_prev
        )
        job_prev = job_parse_log
        job_unroundrobin = urd.build('dataset_unroundrobin', source=job_parse_log)
        job_export_new_csv = urd.build(
            'csvexport',
            filename=f'{base_fn}',
            source=job_unroundrobin,
            separator=';',
            labelsonfirstline=True,
            labels=['time', 'value'],
            sliced=False,
        )
        job_export_new_csv.link_result(f'{base_fn}')
