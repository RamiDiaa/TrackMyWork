import sys,os
from ui_TrackMyWork import Ui_MainWindow

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTime,QTimer ,QDate
from datetime import datetime




class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("TrackMyWork")
        self.setWindowIcon(QIcon('logo.png'))

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_lcd_number)
        self.lcd_milliseconds = 0
        self.lcd_seconds = 0
        self.lcd_minutes = 0
        self.lcd_hours = 0

        self.date_yymmdd = []
        self.current_time_hhmmss = []
        self.duration_hhmmss = []

        self.total_working_duration_hms = []
        

        
        self.ui.lcdnumber_stopwatch.setDigitCount(12)
        self.ui.lcdnumber_stopwatch.display("00:00:00:00")
        current_Qdate=QDate(datetime.now().year,datetime.now().month,datetime.now().day)
        self.ui.dateEdit.setMaximumDate(current_Qdate)
        self.ui.dateEdit.setDate(current_Qdate)
        self.ui.timeEdit_from.setTime(QTime(9,0))
        self.ui.timeEdit_to.setTime(QTime(14,0))

        
        self.display_data()




        self.ui.pushbutton_start.clicked.connect(lambda:self.start_timer())
        self.ui.pushButton_pause.clicked.connect(lambda:self.pause_timer())
        self.ui.pushButton_stop.clicked.connect(lambda:self.reset_timer())
        self.ui.pushButton_submit.clicked.connect(lambda:self.submit_old_work())


    def update_lcd_number(self):
        # self.seconds = (self.milliseconds/100)%60
        # self.minutes = (self.seconds/60)%60
        # print("hours = "+str(self.hours)+": minutes = "+str(self.minutes))
        # self.hourse = (self.minutes/60)%100
        
        # self.ui.lcdnumber_stopwatch.display("{}:{}:{}:{}".format(round(self.hours),round(self.minutes),round(self.seconds),self.milliseconds%100))

        self.ui.lcdnumber_stopwatch.display("{:02d}:{:02d}:{:02d}:{:02d}".format(self.lcd_hours,self.lcd_minutes,self.lcd_seconds,self.lcd_milliseconds))
        
        self.lcd_milliseconds += 1
        if self.lcd_milliseconds == 100:
            self.lcd_milliseconds = 0
            self.lcd_seconds += 1
        if self.lcd_seconds == 60:
            self.lcd_seconds = 0
            self.lcd_minutes += 1
        if self.lcd_minutes == 60:
            self.lcd_minutes =0
            self.lcd_hours += 1
        
    def start_timer(self):
        self.timer.start(10)
    def pause_timer(self):
        self.timer.stop()
    def reset_timer(self):
        self.timer.stop()
        # save data to a file
        str1 = datetime.now().strftime("%y/%m/%d %T") #https://www.ibm.com/docs/en/workload-automation/9.5.0?topic=troubleshooting-date-time-format-reference-strftime
        str2 = "{:02d}:{:02d}:{:02d}:{:02d}".format(self.lcd_hours,self.lcd_minutes,self.lcd_seconds,self.lcd_milliseconds)
        datafile = open("data.txt", "a")
        datafile.write(str1+" "+ str2 +"\n")
        datafile.close()
        
        #then
        self.lcd_hours = self.lcd_minutes = self.lcd_seconds = self.lcd_milliseconds = 0
        self.ui.lcdnumber_stopwatch.display("00:00:00:00")

        self.display_data()


    def submit_old_work(self):
        date = str(self.ui.dateEdit.date().toPyDate()).replace("-","/")
        date = date[2:] #trim 20 of the year

        start_time = self.get_time(str(self.ui.timeEdit_from.time().toPyTime()))
        end_time = self.get_time(str(self.ui.timeEdit_to.time().toPyTime()))


        duration = [j-i for i,j in zip(start_time,end_time)]
        #handeling overflow
        for i in range(2,0,-1):
            if duration[i]< 0 :
                duration[i] += 60
                duration[i-1] -=1

        duration_formated = "{:02d}:{:02d}:{:02d}:00".format(*duration)

        start_time_formated = "{:02d}:{:02d}:{:02d}".format(*start_time)
        print(duration)



        datafile = open("data.txt", "a")
        datafile.write(date + " " + start_time_formated + " " + duration_formated + "\n")
        datafile.close()
        
        print(date)
        print(start_time)
        print(end_time)

        
        self.display_data()
        

    def get_date(self,txt):
        return [int(i) for i in txt.split("/")]
    def get_time(self,txt):
        return [int(i) for i in txt.split(":")]

    def extract_data_from_text(self,txt):
    
        date_time_duration = txt.split()

        date_yymmdd = [int(i) for i in date_time_duration[0].split("/")]
        
        time_hhmmss = [int(i) for i in date_time_duration[1].split(":")]

        duration_hhmmss = [int(i) for i in date_time_duration[2].split(":")]

        return date_yymmdd, time_hhmmss, duration_hhmmss
    
    def display_data(self):
        self.ui.textBrowser.clear() # fix this: clear only when you have to 
        if os.stat("data.txt").st_size ==0:
            self.ui.textBrowser.append("<h1> nothing to see here, go do some work :)</h1>")
            return


        dates,times,durations = self.sort_datafile("data.txt")

        self.ui.textBrowser.append("<h1> Total Working Hours {:02d}:{:02d}:{:02d}:{:02d}</h1>".format(*self.total_working_duration_hms))
        self.ui.textBrowser.append("<h3 style='color:green'>Date: {} ------- Time: {} ------- Duration: {}</h3>".format("yyyy/mm/dd","hh:mm:ss","hh:mm:ss:ms"))
        for i in range(len(dates)):
            self.ui.textBrowser.append("<h3>Date: 20{:02d}/{:02d}/{:02d} -------- Time: {:02d}:{:02d}:{:02d} -------- Duration: {:02d}:{:02d}:{:02d}:{:02d}</h3>".format(*dates[i],*times[i],*durations[i]))

        # self.ui.textBrowser.append("<h1>year: 20{:02d} -- mon:{:02d} -- day: {:02d}</h1>".format(*dates[0]))
        # j,k =1,1
        # for i in range(1,len(dates)):
        #     if dates[i] == dates[i-1]:
        #         self.ui.textBrowser.append("<h2>{:02d}:{:02d}:{:02d}</h2>".format(*times[j]))
        #         self.ui.textBrowser.append("<h3>{:02d}:{:02d}:{:02d}</h3>".format(*durations[k]))
        #         j+= 1
        #         k +=1
        #         continue
        #     self.ui.textBrowser.append("<h1>year: 20{:02d} -- mon:{:02d} -- day: {:02d}</h1>".format(*dates[i]))
        # print("----------")
        # print(dates,times,durations)
        

    def sort_datafile(self,filename):
        datafile = open(filename,"r") #https://mkyong.com/python/python-difference-between-r-w-and-a-in-open/#difference-between-r-r-w-w-a-and-a

        dates,times,durations = [],[],[]
        for line in datafile:
            date_ymd, time_hms, duration_hmsms = self.extract_data_from_text(line)
            dates.append(date_ymd)
            times.append(time_hms)
            durations.append(duration_hmsms)
        datafile.close()

        datafile = open(filename,"w")
        sorted_data = sorted([i+j+k for i,j,k in zip(dates,times,durations)]) #merge lists then sort them and return list of lists

        for list in sorted_data:
            datafile.write("{:02d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d} {:02d}:{:02d}:{:02d}:{:02d}\n".format(*list))
        datafile.close()

        dates,times,durations = [],[],[]
        for list in sorted_data:
            dates.append(list[0:3])
            times.append(list[3:6])
            durations.append(list[6:10])

        # total_hours = sum([i[0] + i[1]/60 + i[2]/(60*60) for i in durations])
        # self.total_hours_hms = [sum([i[0] for i in durations]),sum([i[1] for i in durations]),sum([i[2] for i in durations])]
        self.total_working_duration_hms = [sum(i) for i in zip(*durations)]
        #handeling overflow
        for i in range(2,0,-1):
            if self.total_working_duration_hms[i]> 59 :
                self.total_working_duration_hms[i] -= 60
                self.total_working_duration_hms[i-1] +=1
        print("-------------total hours "+str(self.total_working_duration_hms))

        return dates,times,durations
        


def main():
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()