import argparse, itertools, sys, threading, time
from faster_whisper import WhisperModel

def run_one(name):
    WhisperModel(name)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('models', nargs='+')
    args = parser.parse_args()
    print('This may take several minutes depending on model size.')
    for model in args.models:
        print(f'Preparing model: {model}')
        done = False
        err = None
        def worker():
            nonlocal done, err
            try:
                run_one(model)
            except Exception as e:
                err = e
            finally:
                done = True
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        spinner = itertools.cycle(['.', '..', '...', '....'])
        while not done:
            sys.stdout.write('\rDownloading selected model(s)' + next(spinner) + ' ')
            sys.stdout.flush()
            time.sleep(0.35)
        t.join()
        sys.stdout.write('\r' + ' '*50 + '\r')
        sys.stdout.flush()
        if err:
            raise err
        print(f'Completed: {model}')
    print('Model download step finished.')

if __name__ == '__main__':
    main()
