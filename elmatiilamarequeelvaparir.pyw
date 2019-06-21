import wx
import datetime
import urllib, sys, os, subprocess
try:
  import Tkinter              # Python 2
  import ttk
except ImportError:
  import tkinter as Tkinter   # Python 3
  import tkinter.ttk as ttk

last_perc=-1
cbInterval = []
vars = []
pgInterval = []

def center(toplevel):
    toplevel.update_idletasks()
    w = toplevel.winfo_screenwidth()
    h = toplevel.winfo_screenheight()
    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = w/2 - size[0]/2
    y = h/2 - size[1]/2
    toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))

def setProgress(hour, newValue):
    global w
    global firstHour
    pgInterval[hour-firstHour].config(value=newValue)
    w.update()
    
def report(count, blockSize, totalSize):
    global last_perc
    global current_hour
    percent = int(count*blockSize*100/totalSize)
    if (last_perc != percent and percent>=0 and percent<=100):
        # sys.stdout.write("\r%d%%" % percent + ' complete')
        # sys.stdout.flush()
        last_perc=percent
        setProgress(current_hour, percent)

def get_filename(year,month,day,hour):
    year_str = "%04d" % year
    hour_str = "%02d" % hour
    month_str = "%02d" % month
    day_str = "%02d" % day
    hour_str = "%02d" % hour
    current_hour=hour
    filename=year_str+month_str+day_str+"_"+hour_str+".mp3"
    return filename

def download(year,month,day,hour):
    global current_hour
    year_str = "%04d" % year
    hour_str = "%02d" % hour
    month_str = "%02d" % month
    day_str = "%02d" % day
    hour_str = "%02d" % hour
    current_hour=hour
    print("Downloading "+year_str+"/"+month_str+"/"+day_str+"  " + hour_str + ":00")
    url="http://ondemand.radioflaixbac.cat/podcast/" + year_str + month_str + day_str + hour_str + "0002.mp3?force_download"

    filename=get_filename(year,month,day,hour)
    
    # if filename exists then skip
    
    # urllib.urlretrieve(url, filename)
    # print("  -> filename:"+filename)
    global last_perc
    last_perc=-1
    urllib.urlretrieve(url, filename, reporthook=report)
    if last_perc<=0:
        os.remove(filename)
        global pgInterval
        global firstHour
        s = ttk.Style()
        s.configure("red.Horizontal.TProgressbar", troughcolor ='gray', background='red')
        pgInterval[hour-firstHour].config(style="red.Horizontal.TProgressbar", value=50)
    else:
        global cbInterval
        vars[hour-firstHour].set(0)
    print("\n")

def download_today():
    global firstHour
    global cbInterval
    global pgInterval
    global bDownload
    
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    
    for i in range(len(cbInterval)):
        cbInterval[i].config(state=Tkinter.DISABLED)
        if(vars[i].get()):
            pgInterval[i].config(value=0)
    bDownload.config(state=Tkinter.DISABLED)
    
    for i in range(len(cbInterval)):
        hour=i+firstHour
        if(vars[i].get()):
            download(year,month,day,hour)
    
    for i in range(len(cbInterval)):
        cbInterval[i].config(state=Tkinter.NORMAL)
    bDownload.config(state=Tkinter.NORMAL)


def open_directory():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    subprocess.Popen(r'explorer "'+dir_path+'"')

def clean_older():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    import re
    files = [f for f in os.listdir('.') if re.match(r'[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9]\.mp3', f)]
    
    now = datetime.datetime.now()
    year_str = "%04d" % now.year
    month_str = "%02d" % now.month
    day_str = "%02d" % now.day
    today=year_str + month_str + day_str
    for f in files:
        if f[0:8] < today:
            os.remove(f)
    
    
def main():
    global w
    global current_hour
    global firstHour
    global bDownload
    global pb
    
    current_hour=6
    firstHour=6
    
    w = Tkinter.Tk()
    w.title("El mati i la mare que el va parir - Download poadcast")
    # w.iconbitmap('')
    center(w)

    f = ttk.Frame(w)
    
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    
    for i in range(0,5):
        hour=i+firstHour
        var = Tkinter.IntVar()
        var.set(1)
        txt = "{:02}".format(hour)+":00"
        cb = ttk.Checkbutton(f, text=txt, variable=var)
        cbInterval.append(cb)
        vars.append(var)
        
        pb = ttk.Progressbar(f, orient="horizontal", length=200, mode="determinate")
        pgInterval.append(pb)
        
        filename=get_filename(year,month,day,hour)
        if os.path.isfile(filename):
            statinfo = os.stat(filename)
            if(statinfo.st_size>56000000):
                var.set(0)
                pb.config(value=100)
        
        pb.grid(row=i, column=1)
        cb.grid(row=i, column=0)
        
        f.rowconfigure(i, weight=1)
    
    bDownload = ttk.Button(f, text="Download", command=download_today)
    bDownload.grid(columnspan=2)
    
    bOpenDirectory = ttk.Button(f, text="Open directory", command=open_directory)
    bOpenDirectory.grid(columnspan=2)
    
    bClean = ttk.Button(f, text="Clean older", command=clean_older)
    bClean.grid(columnspan=2)
    
    f.grid(row=0, column=0)
    w.rowconfigure(0, weight=1)
    w.columnconfigure(0, weight=1)
    f.columnconfigure(1, weight=1)
    f.rowconfigure(i+1, weight=1)
    w.minsize(400, 200)
    
    w.mainloop()

if __name__ == '__main__':
  main()