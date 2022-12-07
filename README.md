# 融优学堂自动化脚本

>   仅供学习交流

## Feature

-   自动识别二维码 登录网页界面
-   自动识别未完成课程目录并开始学习未完成课程
-   跳过带有测试的章节

## Usage

-   因为使用selenium库中的Edge Driver, 因此需要安装Edge与相应版本的WebDriver并配置环境变量

-   ```bash
    git clone https://github.com/UltramarineW/RongYouXueTang-Automation-Script.git
    cd RongYouXueTang-Automation-Script
    pip install tqdm selenium ddddocr
    ```

    -   编辑`main.py` 更改其中的username与password

    ```bash
    python main.py
    ```

    

    
