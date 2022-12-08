# By UltramarineW from HIT

import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import time
import ddddocr

# account information
username = ''
password = ''
debug = 0
already_learned_course = []

# setup driver
options = webdriver.EdgeOptions()
options.add_experimental_option("detach", True)
options.add_argument("--mute-audio")
driver = webdriver.Edge(options=options)
driver.maximize_window()


# 处理验证码 调用ddddocr的api
def handleCaptcha():
    try:
        operation = True
        counter = 0
        while operation:
            if counter > 5:
                operation = False
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'yzmmsg'))
            )
            yzmmsg = driver.find_element(By.ID, 'yzmmsg')
            # save captcha for classification
            try:
                yzmmsg.screenshot('./save.png')
            except Exception as e:
                print('验证码截图失败')
                counter += 1
                print(e)
                continue
            ocr = ddddocr.DdddOcr(show_ad=False)
            with open('./save.png', 'rb') as f:
                img_bytes = f.read()
                res = ocr.classification(img_bytes)
            f.close()
            print(f'验证码:{res}')
            driver.find_element(By.ID, 'userYzm').send_keys(res)
            driver.find_element(By.ID, 'login').click()
            counter = counter + 1
            sleep(1)
            operation = False

    except Exception as e:
        print('验证码处理失败')
        print(e)


def loginAccount():
    if username == '' or password == '':
        print('请编辑main.py文件并输入对应的账号和密码')
        exit(-1)
    sleep(1)
    driver.find_element(By.ID, 'usercode').send_keys(username)
    driver.find_element(By.ID, 'password').send_keys(password)
    handleCaptcha()


def findCourse():
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'styu-b-r'))
        )
        class_div = driver.find_element(By.CLASS_NAME, 'styu-b-r')
        # print(f'class_div {class_div}')
        class_div.find_element(By.XPATH, './a[1]').click()
    except Exception as e:
        print('查找<继续学习>失败')
        print(e)


def getContent():
    try:
        left_side = driver.find_element(By.XPATH, '/html/body/div[7]/div[2]/div/div[1]')
        course_list = left_side.find_elements(By.TAG_NAME, 'dd')
        return course_list

    except Exception as e:
        print('获取目录失败')
        print(e)


def playVideo(course):
    try:
        print()
        print('Current learning ', course.text.replace('\n', ' '))
        tag = course.find_element(By.TAG_NAME, 'a')
        tag.click()
        sleep(2)

        iframe_node = driver.find_element(By.NAME, 'zwshow')
        driver.switch_to.frame(iframe_node)
        if debug:
            print('success switch to the frame')

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'sp_index_1'))
        )
        tag = driver.find_element(By.ID, 'sp_index_1')
        if tag.text == '已完成':
            print('本节课已学完')
            return True

        # 点击视频封面中的开始图片
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "video-img"))
        )
        play_button = driver.find_element(By.ID, 'video-img')
        play_button.find_element(By.TAG_NAME, 'a').click()
        print("video start")

        # 找到视频元素
        WebDriverWait(driver, 10).until((
            EC.presence_of_element_located((By.ID, "myVideo_1"))
        ))
        video = driver.find_element(By.ID, "myVideo_1")
        url = driver.execute_script("return arguments[0].currentSrc;", video)
        print(url)

        # 获取播放视频的时间
        duration_time = driver.execute_script("return arguments[0].duration", video)
        current_time = driver.execute_script("return arguments[0].currentTime", video)
        print(f'current_time: {current_time}, duration_time: {duration_time}')

        # tqdm进度条
        pbar = tqdm.tqdm(total=duration_time)
        while current_time <= duration_time:
            last_time = current_time
            current_time = driver.execute_script("return arguments[0].currentTime", video)
            sleep(1)
            pbar.update(current_time - last_time)
        pbar.close()

        tag = driver.find_element(By.ID, 'sp_index_1')
        print(tag.text)
        already_learned_course.append(course.text)
        return True

    except Exception as e:
        print("播放视频失败")
        print(e)
        return False


def judgeExist(element, by, value):
    try:
        element.find_element(by=by, value=value)

    except Exception as e:
        return False
    return True


def chooseCourse(course_list):
    already_learned = []
    not_learned = []
    learning = []

    for course in course_list:
        # 学习过的课程
        if judgeExist(course, By.ID, 'a'):
            already_learned.append(course)
            if debug:
                print('*')
        # 没有学习过的课程
        elif judgeExist(course, By.ID, 'r'):
            if course.text in already_learned_course:
                already_learned.append(course)
                continue
            not_learned.append(course)
            if debug:
                print('o')
        # 正在学习的课程
        else:
            learning.append(course)
            if debug:
                print('-')
    print(f'共有{len(not_learned)}门还未学习的课程, 共有{len(already_learned)}门已经学习的课程')
    return not_learned


def startPlay():
    try:
        while True:
            course_list = getContent()
            not_learned = chooseCourse(course_list)
            course_name = not_learned[0].text
            if len(not_learned) == 0:
                break
            played = playVideo(not_learned[0])
            if debug:
                print(already_learned_course)
            if debug:
                print('hit')
            if played:
                already_learned_course.append(course_name)
            driver.refresh()

    except Exception as e:
        print('播放失败')
        print(e)


if __name__ == '__main__':
    # Login into account
    driver.get('https://cumtb.livedu.com.cn/ispace4.0/moocMainIndex/mainIndex.do')
    login_time_start = time.time()
    driver.find_element(By.CLASS_NAME, 'header-dengl').click()
    loginAccount()
    login_time_end = time.time()
    print('成功登录')
    print(f'Login time:{login_time_end - login_time_start}s')

    # Find course
    findCourse()

    # Start learning course
    startPlay()
