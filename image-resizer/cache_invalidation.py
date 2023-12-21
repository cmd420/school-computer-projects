import os
import time
import json
import schedule
from datetime import datetime, timedelta
from threading import Thread, Lock

mutex = Lock()


class CacheInvalidator:
    def __init__(self, cache_path: str, liftime_min: int = 10) -> None:
        self.cache_path = cache_path
        if not os.path.isdir(cache_path):
            raise ValueError("Invalid cache path.")        

        self.thread = None
        self.has_started = False
        self.liftime_min = liftime_min

    def start(self):
        if self.has_started:
            return
        
        self.has_started = True
        schedule.every(10).seconds.do(self.invalidate)

        self.thread = Thread(target=self.__run_pending)
        self.thread.start()
    
    def stop(self):
        if not self.has_started:
            return
        
        self.has_started = False
        schedule.clear()

    def __run_pending(self):
        while self.has_started:
            schedule.run_pending()
            time.sleep(0.1)

    def update(self, file_path):
        with mutex, open('cache.json', 'r+') as cache_file:
            files: list = json.load(cache_file)
            right_now = str(datetime.now())

            if not any(f['path'] == file_path for f in files):
                entry = {
                    'path': file_path,
                    'last_accessed': right_now
                }

                files.append(entry)
                self.__write(files, cache_file)
                return entry
            
            for idx, file in enumerate(files):
                if file['path'] == file_path:
                    entry = files[idx]
                    entry['last_accessed'] = right_now
                    files[idx] = entry

                    self.__write(files, cache_file)
                    return entry

            raise Exception('This shouldn\'t be possible')
            
    def __write(self, j, f):
        f.seek(0)
        f.write(json.dumps(j))
        f.truncate()


    def invalidate(self):
        print('invalidating cache')
        with mutex, open('cache.json', 'r+') as cache_file:
            files = json.load(cache_file)
            invalid_paths = []
            right_now = datetime.now()

            for file in files:
                path = file['path']
                
                if os.path.exists(path):
                    invalid_paths.append(path)
                    continue

                last_accessed = datetime.strptime(file['last_accessed'], '%Y-%m-%d %H:%M:%S.%f')
                
                if (last_accessed - right_now).seconds > (self.liftime_min * 60):
                    invalid_paths.append(path)

            print('invalid files:', invalid_paths)
            for p in invalid_paths:
                try:
                    os.remove(p)
                except:
                    pass

            files = list(filter(lambda f: f['path'] in invalid_paths, files))
            self.__write(files, cache_file)


                