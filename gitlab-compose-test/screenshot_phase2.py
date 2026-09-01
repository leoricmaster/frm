#!/usr/bin/env python3
"""二阶段截图：Harbor 双项目与推拉记录、MinIO 三桶与投放区、两条流水线证据。
复用第一阶段模式：chromium at /usr/bin/google-chrome，viewport 1440×900。

选择器现场探测结论（2026-09-01）：
  GitLab  : input[name='user[login]'] / input[name='user[password]'] / button[type='submit']（同 screenshot.py）
  Harbor  : UI 登录 /c/login 受 CSRF origin 校验返回 403 "origin invalid"（HeadlessChrome Origin 头
            不被 Harbor gorilla/csrf 接受）；改用 Authorization: Basic 头直接访问受保护页面，
            SPA 以 admin 身份渲染，效果等同登录。项目 URL 用数字 ID：frm-ci=2、docker-hub-proxy=3。
  MinIO   : input#accessKey / input#secretKey / button#do-login；桶导航无 <a> 锚，React onClick
            在 button#manageBucket-<name> 上，page.click 受 actionability 限制不触发路由，
            改用 page.eval_on_selector(...).click() 原生触发；实际桶浏览路由为 /browser/<name>
            （非简报预估的 /buckets/<name>/browse）。
"""
import base64, json, os, time, urllib.request
from playwright.sync_api import sync_playwright

OUT = "/home/lancer/projects/frm/gitlab-compose-test/screenshots"
GL = "http://127.0.0.1:8081"
HB = "http://10.66.35.35:8084"
MN = "http://10.66.35.35:9003"
GL_PAT = "glpat-dsd8nyjb7efZJJ-g4_uRrW86MQp1OjEH.01.0w1o12cfg"
HB_BASIC = base64.b64encode(b"admin:Harbor#2026Proto").decode()

os.makedirs(OUT, exist_ok=True)


def gl_api(path):
    req = urllib.request.Request(f"{GL}/api/v4{path}", headers={"PRIVATE-TOKEN": GL_PAT})
    return json.load(urllib.request.urlopen(req))


def shot(page, fname, url, label, wait="domcontentloaded", sleep=1.8):
    """goto + 截图；失败不阻塞。"""
    try:
        page.goto(url, wait_until=wait, timeout=20000)
        time.sleep(sleep)
        page.screenshot(path=f"{OUT}/{fname}.png", full_page=False)
        print(f"[OK]   {fname} — {label}")
        return True
    except Exception as e:
        print(f"[FAIL] {fname} — {label}: {str(e)[:120]}")
        return False


def gl_shot(page):
    """GitLab 侧：登录 + perception/firmware 流水线与 job 日志。"""
    page.goto(f"{GL}/users/sign_in", wait_until="networkidle")
    page.fill("input[name='user[login]']", "root")
    page.fill("input[name='user[password]']", "Excavator#2026Proto")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    time.sleep(2)

    # 动态查最新绿 pipeline 与 job id
    pl = gl_api("/projects/excavator%2Fautonomy%2Fperception/pipelines?per_page=1")[0]
    jobs = gl_api(f"/projects/excavator%2Fautonomy%2Fperception/pipelines/{pl['id']}/jobs")
    fw = gl_api("/projects/excavator%2Ffirmware%2Fhydraulic-controller/pipelines?per_page=1")[0]
    fjobs = gl_api(f"/projects/excavator%2Ffirmware%2Fhydraulic-controller/pipelines/{fw['id']}/jobs")
    job_by_name = {j["name"]: j for j in jobs}
    fjob_by_name = {j["name"]: j for j in fjobs}
    print(f"[info] perception pipeline #{pl['id']} ({pl['status']}); "
          f"fetch-dataset={job_by_name['fetch-dataset']['id']}, "
          f"train-model={job_by_name['train-model']['id']}")
    print(f"[info] firmware pipeline #{fw['id']} ({fw['status']}); "
          f"image-build={fjob_by_name['image-build']['id']}")

    base = f"{GL}/excavator/autonomy/perception/-"
    fwbase = f"{GL}/excavator/firmware/hydraulic-controller/-"

    shot(page, "21-perception-pipelines", f"{base}/pipelines", "perception 流水线列表")
    shot(page, "22-perception-green",     f"{base}/pipelines/{pl['id']}",
         f"perception 最新流水线 #{pl['id']} 全绿详情")
    shot(page, "23-fetch-dataset-job",    f"{base}/jobs/{job_by_name['fetch-dataset']['id']}",
         "fetch-dataset job 日志（MinIO 拉取+sha256 校验+masked 变量）")
    shot(page, "24-train-model-job",      f"{base}/jobs/{job_by_name['train-model']['id']}",
         "train-model job 日志（推 training-output+manifest 指针）")
    shot(page, "25-fw-image-build-job",   f"{fwbase}/jobs/{fjob_by_name['image-build']['id']}",
         "firmware image-build job 日志（docker push/pull Harbor）")


def hb_shot(browser):
    """Harbor 侧：用 Basic auth 头直接访问受保护页面（UI 登录受 CSRF origin 限制不可用）。

    Harbor /c/login 对 HeadlessChrome 的 Origin 头返回 403 "origin invalid"
    （gorilla/csrf 比对 EXT_ENDPOINT 不通过）；但 API 与 SPA 均接受 Authorization:
    Basic 头，因此以 admin 身份直接渲染各页，效果等同登录后截图。
    """
    ctx = browser.new_context(viewport={"width": 1440, "height": 900},
                              ignore_https_errors=True,
                              extra_http_headers={"Authorization": f"Basic {HB_BASIC}"})
    page = ctx.new_page()

    shot(page, "26-harbor-projects", f"{HB}/harbor/projects",
         "Harbor 项目列表（frm-ci + docker-hub-proxy）", wait="networkidle", sleep=3)
    # frm-ci = project id 2；docker-hub-proxy = project id 3
    shot(page, "27-harbor-frmci",    f"{HB}/harbor/projects/2/repositories",
         "frm-ci 镜像仓（CI 推送的 ci-base）", wait="networkidle", sleep=3)
    shot(page, "28-harbor-proxy",    f"{HB}/harbor/projects/3/repositories",
         "代理缓存项目（busybox/alpine/python 缓存记录）", wait="networkidle", sleep=3)
    ctx.close()


def mn_shot(page):
    """MinIO 侧：登录 + 三桶总览 + 两个关键桶内容。

    桶浏览路由为 /browser/<name>（非 /buckets/<name>/browse）；React onClick 在
    button#manageBucket-<name> 上，page.click 受 actionability 限制不触发路由，
    改用 page.eval_on_selector 原生 .click()。
    """
    page.goto(f"{MN}/login", wait_until="networkidle")
    time.sleep(2)
    page.fill("input#accessKey", "minioadmin")
    page.fill("input#secretKey", "Excavator#2026Proto")
    page.click("button#do-login")
    page.wait_for_load_state("networkidle")
    time.sleep(3)

    # 29: 三桶总览
    shot(page, "29-minio-buckets", f"{MN}/buckets",
         "MinIO 三桶总览", wait="networkidle", sleep=3)

    def click_bucket(name):
        """回到 /buckets 列表，JS 点击指定桶进入浏览页。"""
        if page.url != f"{MN}/buckets":
            page.goto(f"{MN}/buckets", wait_until="networkidle")
            time.sleep(2)
        sel = f"button#manageBucket-{name}"
        page.eval_on_selector(sel, "el => el.click()")
        time.sleep(3)

    # 30: dataset-model
    try:
        click_bucket("dataset-model")
        page.screenshot(path=f"{OUT}/30-minio-dataset.png")
        print(f"[OK]   30-minio-dataset — dataset-model（数据集+现场归档）")
    except Exception as e:
        print(f"[FAIL] 30-minio-dataset: {str(e)[:120]}")

    # 31: training-output
    try:
        click_bucket("training-output")
        page.screenshot(path=f"{OUT}/31-minio-training.png")
        print(f"[OK]   31-minio-training — training-output（模型权重+manifest）")
    except Exception as e:
        print(f"[FAIL] 31-minio-training: {str(e)[:120]}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/google-chrome")
        # GitLab 与 MinIO 共用一个 context（同 viewport），Harbor 单独 context 带 Basic auth 头
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, ignore_https_errors=True)
        page = ctx.new_page()
        gl_shot(page)
        mn_shot(page)
        ctx.close()
        hb_shot(browser)
        browser.close()
    print("[done] phase2 截图结束")


if __name__ == "__main__":
    main()
