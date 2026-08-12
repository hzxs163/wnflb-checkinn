# -*- coding: utf8 -*-
import os
import requests

def send_notification(title: str, content: str):
    """
    多渠道通知聚合
    环境变量为空自动跳过该渠道
    支持：Telegram、Bark、Gotify、WxPusher、企业微信机器人、NotifyX、通用Webhook、虾推啥
    """

    # -------------------------- Telegram (HTML模式) --------------------------
    tg_bot_token = os.getenv("TG_BOT_TOKEN", "").strip()
    tg_chat_id = os.getenv("TG_CHAT_ID", "").strip()
    if tg_bot_token and tg_chat_id:
        try:
            url = f"https://api.telegram.org/bot{tg_bot_token}/sendMessage"
            html_text = f"<b>{title}</b>\n<pre>{content}</pre>"
            payload = {
                "chat_id": tg_chat_id,
                "text": html_text,
                "parse_mode": "HTML"
            }
            requests.post(url, json=payload, timeout=15)
        except Exception as e:
            print(f"[Telegram推送异常] {str(e)}")

    # -------------------------- Bark --------------------------
    bark_url = os.getenv("BARK_URL", "").strip()
    if bark_url:
        try:
            payload = {"title": title, "body": content}
            requests.post(bark_url, json=payload, timeout=15)
        except Exception as e:
            print(f"[Bark推送异常] {str(e)}")

    # -------------------------- Gotify 修复：全部改为英文半角符号 --------------------------
    gotify_url = os.getenv("GOTIFY_URL", "").strip()
    gotify_token = os.getenv("GOTIFY_TOKEN", "").strip()
    if gotify_url and gotify_token:
        try:
            url = f"{gotify_url.rstrip('/')}/message"
            payload = {"title": title, "message": content, "priority": 5}
            headers = {"X-Gotify-Key": gotify_token}
            requests.post(url, json=payload, headers=headers, timeout=15)
        except Exception as e:
            print(f"[Gotify推送异常] {str(e)}")

    # -------------------------- WxPusher --------------------------
    wxpusher_token = os.getenv("WXPUSHER_TOKEN", "").strip()
    wxpusher_uids = os.getenv("WXPUSHER_UIDS", "").strip()
    if wxpusher_token and wxpusher_uids:
        try:
            uids = [u.strip() for u in wxpusher_uids.split(",") if u.strip()]
            payload = {
                "appToken": wxpusher_token,
                "content": f"**{title}**\n{content}",
                "uids": uids,
                "contentType": 3
            }
            requests.post("https://wxpusher.zjiecode.com/api/send/message", json=payload, timeout=15)
        except Exception as e:
            print(f"[WxPusher推送异常] {str(e)}")

    # -------------------------- 企业微信机器人 --------------------------
    wecom_webhook = os.getenv("WECOM_WEBHOOK", "").strip()
    if wecom_webhook:
        try:
            payload = {
                "msgtype": "markdown",
                "markdown": {"content": f"**{title}**\n{content}"}
            }
            requests.post(wecom_webhook, json=payload, timeout=15)
        except Exception as e:
            print(f"[企业微信推送异常] {str(e)}")

    # -------------------------- NotifyX --------------------------
    notifyx_url = os.getenv("NOTIFYX_URL", "").strip()
    notifyx_token = os.getenv("NOTIFYX_TOKEN", "").strip()
    if notifyx_url and notifyx_token:
        try:
            url = f"{notifyx_url.rstrip('/')}/api/push"
            payload = {"token": notifyx_token, "title": title, "message": content}
            requests.post(url, json=payload, timeout=15)
        except Exception as e:
            print(f"[NotifyX推送异常] {str(e)}")

    # -------------------------- 通用Webhook --------------------------
    generic_webhook = os.getenv("GENERIC_WEBHOOK", "").strip()
    if generic_webhook:
        try:
            payload = {"title": title, "body": content, "msg": content}
            requests.post(generic_webhook, json=payload, timeout=15)
        except Exception as e:
            print(f"[通用Webhook推送异常] {str(e)}")

    # -------------------------- 虾推啥 xiatuishe --------------------------
    xts_token = os.getenv("XIATUISHE_TOKEN", "").strip()
    xts_server = os.getenv("XIATUISHE_SERVER", "https://wx.xtuis.cn").strip()
    if xts_token:
        print("[虾推啥] 检测到token，开始发起推送")
        try:
            url = f"{xts_server}/{xts_token}.send"
            params = {
                "text": title,
                "desp": content[:500]
            }
            resp = requests.get(
                url,
                params=params,
                timeout=10,
                headers={"User-Agent": "AutoCheckin/1.0"}
            )
            if resp.status_code == 200:
                res_text = resp.text.strip()
                if any(k in res_text.lower() for k in ("success", "ok", "成功")):
                    print("[虾推啥] 推送成功")
                else:
                    print(f"[虾推啥] 返回: {res_text}")
            else:
                print(f"[虾推啥] HTTP错误 status={resp.status_code}")
        except requests.exceptions.Timeout:
            print("[虾推啥] 推送超时")
        except requests.exceptions.ConnectionError:
            print("[虾推啥] 连接失败")
        except Exception as e:
            print(f"[虾推啥] 推送异常: {str(e)}")

    # 全部渠道判断，全部使用普通字符串，杜绝全角符号干扰
    all_env = [
        tg_bot_token, tg_chat_id, bark_url,
        gotify_url, gotify_token, wxpusher_token, wxpusher_uids,
        wecom_webhook, notifyx_url, notifyx_token, generic_webhook,
        xts_token
    ]
    if not any(all_env):
        print("  (未配置推送通知)")
