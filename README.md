# Filter Papers with Code

Use Python web scraping to apply advanced filtering on [Papers with Code](https://paperswithcode.com/).

## How to Use

1. Clone the repository.

```shell
git clone https://github.com/ColeBallard/Filter-Papers-with-Code
```

2. Download [Python 3.12](https://www.python.org/downloads/). (Other versions will likely work fine).

3. Create the Virtual Environment.

```shell
python -m venv venv
```

4. Activate the Virtual Environment.

Windows (Command Prompt):

```shell
venv\Scripts\activate
```

Windows (PowerShell):

```shell
venv\Scripts\Activate.ps1
```

macOS/Linux:

```shell
source venv/bin/activate
```

5. Install the requirements.

```shell
pip install -r requirements.txt
```

6. Download the [ChromeDriver](https://googlechromelabs.github.io/chrome-for-testing/).

7. Create a file in the project root folder called `config.yaml`. In this file, specify the file path for your downloaded ChromeDriver executable.

```yaml
ChromeDriverPath: 'path/to/chromedriver.exe'
```

8. Adjust parameters and function calls in `main.py` to specify your advanced filtering.

9. Run `main.py` and check the console output.

```shell
python main.py
```