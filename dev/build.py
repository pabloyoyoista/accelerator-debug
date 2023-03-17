import glob
from os.path import basename, join
from accelerator.colour import bold

def main(urd):
    fns = sorted(glob.glob(join(urd.info.input_directory, "*.csv")))

    urdkey = 'myimport'  # See comment 3
#    urd.truncate(urdkey, 0)  # un-comment if you need to re-run, See comment 0.
    last_ix = urd.peek_latest(urdkey).timestamp
    for ix, fn in enumerate(fns, 1):
        if ix <= int(last_ix):
            # see comment 1. below
            continue
        base_fn = basename(fn)
        print(bold(base_fn))
        urd.begin(urdkey, ix, caption=base_fn)
        prev = urd.get(urdkey, ix - 1).joblist  # See comment 2 about timestamp-formats
        job_import_log = urd.build(
            'csvimport',
            filename=fn,
            comment='#',
            labels=['data'],
            separator='',
            previous=prev.get('csvimport'),
        )
        job_parse_log = urd.build(
            'log_parser', source=job_import_log, previous=prev.get('job_parse_log')
        )
        job_unroundrobin = urd.build('dataset_unroundrobin', source=job_parse_log)
        job_export_new_csv = urd.build(
            'csvexport',
            filename=f'{base_fn}',
            source=job_unroundrobin,
            separator=';',
            labelsonfirstline=True,
            labels=['time', 'value'],
            sliced=False,
            previous=prev.get('csvexport')
        )
        job_export_new_csv.link_result(f'{base_fn}')
        urd.finish(urdkey)


# Try:
#   ax urd                   # to see all urdkeys
#   ax urd myimport/         # to see all sessions (as timestamp + caption) for the myimport urdlist
#   ax urd myimport          # to see joblist of latest urd entry
#   ax urd myimport/1        # to see joblist of urd entry at timestamp 1
#
# Then you can do things like
#   ax job :myimport/2:csvexport  # to see info about the csveport job at timestamp 2 of urdlist myimport (!)
#
# Don't forget to point your browser to the accelerator board!


# Comment 0
#
# truncate() will set a restart-marker in the urd log file.
# It will then appear as if the urd list is empty (if called
# with timestamp=0), but all earlier entries are still in
# the transaction log if you need them!


# Comment 1.
#
# Two option here:
#
# 1.  including this if-statement.  Then, immediately skip to
#     next timestamp if this timestamp already exists in urd.
#
#     Pros:  - Faster, if many many jobs,
#     Cons:  - Jobs will not be re-run if source is modified,
#              since build()-calls are skipped.
#
# 2.  remove the if-statement.  Then, all build-calls will be
#     run for all input files.
#
#     If the timestamp is already in urd, the urd.finish-call
#     will fail if it contains jobs different from the ones
#     stored at the timestamp already.  This could be a way
#     to validate that the current version of the source code
#     is the same as the version used to create the urd entries.
#
#     Cons:  - slower if many jobs.


# Comment 2
# The timestamp in this script is an integer from 1 and onwards.
# But you can also use dates or datetimes.  Actually, it can
# even be a tuple (date, integer) if there are many files "at
# the same time" for example.
#
# I think you should think of a way to assign timestamps to
# each entry here, ideally something derived from the filename
# or similar.


# Comment 3
# Use different urd-keys to distinguish between different
# data.  For example, you can have one urdkey per equipment,
# per language, or per country...
