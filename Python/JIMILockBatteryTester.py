from selenium import webdriver
from time import sleep
import re
from time import localtime, strftime
import csv

class Lifecycle:
    def __init__(self, driver):
        self.driver = driver
        self.url = "https://iot-lifecycle.yellow.tech/"        
        
    def navigate(self):
        self.driver.get(self.url + "smartlock_command")

    def login(self, username='admin', password='admin'):
        self.driver.get("https://accounts.google.com/signin")        
        self.driver.find_element_by_name("identifier").send_keys(username)
        self.driver.find_element_by_xpath("//*[@id='identifierNext']/span/span").click()
        self.driver.implicitly_wait(4)
        self.driver.find_element_by_name('password').send_keys(password)
        element = self.driver.find_element_by_xpath("//*[@id='passwordNext']/span/span")
        self.driver.execute_script("arguments[0].click()", element)
        
        self.driver.get(self.url)
        self.driver.find_element_by_xpath("//a[@href='/auth/google_oauth2']").click()
        
    def sendcommand(self, id, command):
        self.driver.find_element_by_name("identifier").send_keys(id)
        self.driver.find_element_by_name("command").send_keys(command)
        self.driver.find_element_by_name("commit").click()      
        sleep(2)
        return self.driver.find_element_by_xpath("/html/body/div/div[2]/pre").text


class SmartLock:
    def __init__(self, lifeCycle):
        self.lifeCycle = lifeCycle
        self.sampleTime = []
        self.gsmSignalStrength = "None"
        self.voltageLevel = []
        self.batteryLevel = 0        
        self.latitude = 0
        self.longitude = 0
        self.response = "None"        


    def statusCommand(self, id):
        self.response = self.lifeCycle.sendcommand(id, "STATUS")
        m = re.search('"lockerAnswer": "Battery:(.+)V.*GSM Signal Level:([A-Za-z]+)', self.response)
        if m:            
            v = float(m.group(1))
            self.voltageLevel.append(v)
            self.sampleTime.append(strftime("%Y-%m-%d %H:%M:%S", localtime()))
            self.gsmSignalStrength = m.group(2)
            self.batteryLevel = (v - 3.5) / (4.2 - 3.5) * 100
        else:
            self.gsmSignalStrength = "None"
            self.voltageLevel.append(0)
            self.batteryLevel = 0            

    def VCPLockCommand(self, id):
        self.response = self.lifeCycle.sendcommand(id, "VCP_LOCK,1")
    
    def VCPUnlockCommand(self, id):
        self.response = self.lifeCycle.sendcommand(id, "VCP_LOCK,0")


class BatteryTest:
    def __init__(self, smartlock):
        self.sm = smartlock

    def start(self, id, interval, testTime):
        print("Starting test with {}s interval during {}h".format(interval, int(testTime / 3600)))
        for i in range(0, int(testTime / interval)):    
            self.sm.statusCommand(id)
            print("#{}: {} -->> {:.2f}v = {:.2f}%".format(i, self.sm.sampleTime[-1], self.sm.voltageLevel[-1], self.sm.batteryLevel) )     
            sleep(interval)

    def saveResult(self, filePath):
        print("Saving test result in {}".format(filePath))
        with open(filePath, 'w', newline='\n') as fileOut:
            wr = csv.writer(fileOut, quoting=csv.QUOTE_ALL)
            title = ["timestamp", "voltage", "percentage"]
            wr.writerow(title)
            for t,v in zip(self.sm.sampleTime, self.sm.voltageLevel):
                row = [t, v, (v - 3.5) / (4.2 - 3.5) * 100]
                wr.writerow(row)    
        fileOut.close()


options = webdriver.ChromeOptions()
options.add_argument("allow-file-access-from-files")
options.add_argument("use-fake-device-for-media-stream")
options.add_argument("use-fake-ui-for-media-stream") 
browser = webdriver.Chrome("C:/Users/Douglas Reis/Downloads/chromedriver_win32/chromedriver.exe", options=options)

lf = Lifecycle(browser)
lf.navigate()
lf.login("douglas.reis@grow.mobi", "GrowR315")
sleep(2)
lf.navigate()
sm = SmartLock(lf)
bt = BatteryTest(sm)

try:
    bt.start("30848258", 5 * 60, 3 * 24 * 60 * 60 )
        
finally:    
    bt.saveResult("output.csv")        

browser.close()