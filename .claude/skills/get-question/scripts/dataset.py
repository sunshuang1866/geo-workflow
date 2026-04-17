from hmac import new
from httpx import head
from pyparsing import C
import requests
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import logging
from tqdm import tqdm


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

Cookie = ""
Token = ""
def _login():
    print("正在登录获取权限...")
    if Cookie and Token:
        return Cookie, Token
    try:
        response = requests.post(
            "https://id.datastat.osinfra.cn/oneid/login",
            headers={
                "Referer": "https://id.datastat.osinfra.cn/"
            },
            json={
                "permission": "sigRead",
                "account": "hourunze@h-partners.com",
                "client_id": "682e93df3c292532ad012ff7",
                "accept_term": 0,
                "password": "2bee5ecebe25622435f72da679ba58ee76c5ddde583cdd65fba5836d54485af4de58d5fc7db495abe63d67803cde718773e07f0c5af362229b377efe3bbfe07a9eb79f63d3df611acabd3cb8a57620b2a9a2470ec33f204089b4a19bb6c3e777df2882e6130622edc6bb00435eba5dba6442255f8348404435768b017576e631",
            },
            timeout=3000,
        )
        print(response.json())
        Cookie1 = ""
        Token1 = ""
        for k, v in response.cookies.items():
            Cookie1 += f"{k}={v};"
            if k == "_U_T_":
                Token1 = v
        return Cookie1, Token1
    except Exception as e:
        logging.error(f"Login failed: {e}")
        return "", ""

community = "openubmc"
issue_trigger = 0
forum_trigger = 1
def update_source_status():
    conn = None
    dbConfigMap = {
        "openubmc": {
            "host": "27.106.99.76",
            "port": "5432",
            "dbname": "openubmc_hotopic_data_clean",
            "user": "openubmc_hotopic",
            "password": "axr2M!D27bs7NK!32ur5"
        },
        "vllm": {
            "host": "27.106.99.76",
            "port": "5432",
            "dbname": "vllm_hotopic_data_clean",
            "user": "vllm_hotopic",
            "password": "B!Dclkv!1D6zCD3t"
        },
        "vllm-ascend": {
            "user": "vllm_ascend_hotopic",
            "password": "!h9E6qL!4P2vX7Z!bM1rT5dN",
            "host": "27.106.99.76",
            "port": "5432",
            "dbname": "vllm_ascend_hotopic_data_clean"
        },    
        "mindspore": {
            "host": "27.106.99.76",
            "port": "5432",
            "dbname": "mindspore_hotopic_data_clean",
            "user": "mindspore_hotopic",
            "password": "S7mx!mT752e2!ZxVaL3!"
        },        
        "openeuler": {
            "host": "27.106.99.76",
            "port": "5432",
            "dbname": "openeuler_hotopic_data_clean",
            "user": "openeuler_hotopic",
            "password": "84F!X6OZe!gAaiB7Ksv!"        
        },        
        "cann": {
            "host": "27.106.99.76",
            "port": "5432",
            "dbname": "cann_hotopic_data_clean",
            "user": "cann_hotopic",
            "password": "L!rADDVE2m!0S0Wu"
        },
        "opengauss" : {
            "host": "27.106.99.76",
            "port": "5432",
            "dbname": "opengauss_hotopic_data_clean",
            "user": "opengauss_hotopic",
            "password": "Y0kVbz75Z6ePwHp!"
        },
        "cannopen" : {
            "host": "27.106.99.76",
            "port": "5432",
            "dbname": "cannopen_hotopic_data_clean",
            "user": "cannopen_hotopic",
            "password": "5beK3qcm!!6bvH+h"
        },
        "mindspore": {
            "host": "27.106.99.76",
            "port": "5432",
            "dbname": "mindspore_hotopic_data_clean",
            "user": "mindspore_hotopic",
            "password": "S7mx!mT752e2!ZxVaL3!"
        },
        "mindcluster": {
            "host": "27.106.99.76",
            "port": "5432",
            "dbname": "mindcluster_hotopic_data_clean",
            "user": "mindcluster_hotopic",
            "password": "Hdgab7z!wJ!8i!K3"
        },
        "mindie": {
            "host": "27.106.99.76",
            "port": "5432",
            "dbname": "mindie_hotopic_data_clean",
            "user": "mindie_hotopic",
            "password": "cR6zr!rxGbNToVfj"
        },
        "mindsdk": {
            "host": "27.106.99.76",
            "port": "5432",
            "dbname": "mindsdk_hotopic_data_clean",
            "user": "mindsdk_hotopic",
            "password": "E!jiud5YausLYMwh"
        },
        "mindspeed": {
            "host": "27.106.99.76",
            "port": "5432",
            "dbname": "mindspeed_hotopic_data_clean",
            "user": "mindspeed_hotopic",
            "password": "4r!T!dxtX0W+RZd9"
        },
        "mindstudio": {
            "host": "27.106.99.76",
            "port": "5432",
            "dbname": "mindstudio_hotopic_data_clean",
            "user": "mindstudio_hotopic",
            "password": "KE!gTxQs1mu!LN!i"
        },
        "pta": {
            "host": "27.106.99.76",
            "port": "5432",
            "dbname": "pta_hotopic_data_clean",
            "user": "pta_hotopic",
            "password": "9El!4gd!G4efL6PY"
        },
        "sgl": {
            "host": "27.106.99.76",
            "port": "5432",
            "dbname": "sglang_hotopic_data_clean",
            "user": "sglang_hotopic",
            "password": "Xu8Ai!g5BsGg!NEh"
        },
        "tilelang": {
            "host": "27.106.99.76",
            "port": "5432",
            "dbname": "tilelang_hotopic_data_clean",
            "user": "tilelang_hotopic",
            "password": "g0!28vhJxv+KPk3J"
        },
        "triton": {
            "host": "27.106.99.76",
            "port": "5432",
            "dbname": "triton_hotopic_data_clean",
            "user": "triton_hotopic",
            "password": "hc4!!g4HTHwD23T6"
        },
        "unifiedbus": {
            "host": "27.106.99.76",
            "port": "5432",
            "dbname": "unifiedbus_hotopic_data_clean",
            "user": "unifiedbus_hotopic",
            "password": "vtfKkQ!2RQ!e4NbWB2Xq"
        },
        "verl": {
            "host": "27.106.99.76",
            "port": "5432",
            "dbname": "verl_hotopic_data_clean",
            "user": "verl_hotopic",
            "password": "I8v3hh8TE!vEkQKb"
        },
        "pytorch": {
            "host": "27.106.99.76",
            "port": "5432",
            "dbname": "pytorch_hotopic_data_clean",
            "user": "pytorch_hotopic",
            "password": "X!Je!PUQnGFvqdvu"
        },
        "ascendnpuir": {
            "host": "27.106.99.76",
            "port": "5432",
            "dbname": "ascendnpuir_hotopic_data_clean",
            "user": "ascendnpuir_hotopic",
            "password": "4lr9lj!O!+8sgTyz"
        },
        "openfuyao": {
            "user": "openfuyao_hotopic",
            "password": "d4!le8jiZ!7di!9a",
            "host": "27.106.99.76",
            "port": "5432",
            "dbname": "openfuyao_hotopic_data_clean"
        }
    }
    try:
        dbConfig = dbConfigMap[community]
        conn = psycopg2.connect(
            dbname=dbConfig["dbname"],
            user=dbConfig["user"],
            password=dbConfig["password"],
            host=dbConfig["host"],
            port=dbConfig["port"]
        )
        cursor = conn.cursor()

        if issue_trigger:
            cursor.execute("""
                SELECT id, url 
                FROM discussion 
                WHERE is_deleted = False and source_type='issue'
            """)

            # 遍历所有记录
            records = cursor.fetchall()
            for record_id, url in tqdm(records, desc="更新数据状态"):
                print(record_id, url)
                try:
                    new_status = check_issue_status(url)
                    # 更新数据库状态
                    update_query = sql.SQL("""
                        UPDATE discussion 
                        SET source_closed = %s 
                        WHERE id = %s
                    """)
                    cursor.execute(update_query, (new_status, record_id))
                    conn.commit()
                    if new_status:
                        print(f"更新记录 {record_id} 状态为 {new_status}, url: {url}")

                except Exception as e:
                    print(f"处理记录 {record_id} 失败: {str(e)}")
                    conn.rollback()
        if forum_trigger:
            cursor.execute("""
                SELECT id, url 
                FROM discussion 
                WHERE is_deleted = False and source_type='forum'
            """)
            records = cursor.fetchall()
            for record_id, url in tqdm(records, desc="更新数据状态"):
                try:
                    new_status = check_forum_status(url)
                    print(record_id, new_status)
                    # 更新数据库状态
                    update_query = sql.SQL("""
                        UPDATE discussion 
                        SET source_closed = %s 
                        WHERE id = %s
                    """)
                    cursor.execute(update_query, (new_status, record_id))
                    conn.commit()
                    if new_status:
                        print(f"更新记录 {record_id} 状态为 {new_status}, url: {url}")

                except Exception as e:
                    print(f"处理记录 {record_id} 失败: {str(e)}")
                    conn.rollback()

    except Exception as e:
        logging.error(f"数据库操作失败: {str(e)}")
    finally:
        if conn:
            conn.close()

def check_forum_status(url):
    detail_url = f"https://beta.datastat.osinfra.cn/server/customization/{community}/detail/v2"
    payload = {
        "community": community,
        "dim": ["uuid", "title", "last_update_time", "url", "status", "has_accepted_answer", "closed", "closed_at", "tags", "category_id"],
        "name": f"fact_{community}_forum_topic" if community != "cannopen" else "fact_cann_forum_topic",
        "page": 1,
        "page_size": 100,
        "filters": [
            {
                "column": "url",
                "operator": "=",
                "value": f"{url}"
            }
        ],
        "conditonsLogic": "AND",
        "order_field": "uuid",
        "order_dir": "ASC"
    }
    headers = {
        "access-token": "jvMe0-mMVNXp4k_OkmpdHPByVuyCpMgCLoGV3Hm61ps"
    }
    response = requests.post(detail_url, json=payload, headers=headers)
    if response.json().get('code') in [401, 403]:
        logging.error("token无效，登录失败，获取讨论源状态失败")
        return False
    if response.json().get('code') == 429:
        logging.info("发生限流，等待中")
        time.sleep(1)
        return self.check_forum_status(community, uuid)
    detail_data = response.json()
    print(detail_data)
    if detail_data.get('data'):
        data = detail_data.get('data')[0]
        if data.get("status") in ["resolved", "closed"]:
            return True
    return False

def check_issue_status(html_url):
    detail_url = f"https://beta.datastat.osinfra.cn/server/customization/{community}/detail/v2"
    payload = {
        "community": f"{community}",
        "dim": [],
        "name": f"dws_{community}_contribute",
        "page": 1,
        "page_size": 100,
        "filters": [
            {
                "column": "html_url",
                "operator": "=",
                "value": f"{html_url}"
            }
        ],
        "conditonsLogic": "AND",
        "order_field": "uuid",
        "order_dir": "ASC"
    }
    global Token, Cookie
    headers = {
        'Cookie': Cookie,
        'token': Token
        }
    response = requests.post(detail_url, json=payload, headers=headers)
    if response.json().get('code') in [401, 403]:
        print(html_url)
        cookie, token = _login()
        if token:    
            Cookie = cookie
            Token = token
            headers = {
                "Cookie": Cookie,
                "token": Token
            }
            response = requests.post(detail_url, json=payload, headers=headers)
        else:
            logging.error("重新登录失败")
            return False
    detail_data = response.json()
    print(detail_data)
    if detail_data.get('data'):
        data = detail_data.get('data')[0]
        if data.get("state") == "closed":
            return True
    return False
    

if __name__ == "__main__":
    update_source_status()
