from email import header
from pathlib import Path
import requests
import lxml.html
from typing import Dict
from single_source import get_version
import time

__version__ = get_version(__name__, Path(__file__).parent.parent)

# 医療機関であるかの確認画面に遷移する対策
__session__ = requests.session() 
__session__.post("https://www.askul.co.jp/ctg/medical/medicalConfirm/clickYes", data = {'backUrl': '/'})


def get_item_info(product_code:str)->Dict[str, str]:
    """
    アスクルのページから商品情報を取得する
    
    Args:
        product_code: 商品コード
    
    Return:
        dict: 商品情報
    """
    item_url = "https://www.askul.co.jp/p/" + product_code + "/"
    item_info = {"product_code": product_code}
    item_info["error_message"] = ""
    item_info["success"] = False

    for i in range(3):
        try:
            res = __session__.get(item_url, timeout=10)

            html = lxml.html.fromstring(res.text)

            # 取扱中止等のエラーがある場合は商品名にエラーメッセージを入れて終了
            if len(html.xpath('//div[@class="errorMessageInner"]'))>0:
                item_info["item_name"] = html.xpath('//div[@class="errorMessageInner"]')[0].text_content().strip()
                item_info["error_message"] = item_info["item_name"]
                return item_info
            
            head_breadcrumbs = html.xpath('//div[@class="breadcrumbs"]')[0]
            elms = head_breadcrumbs.xpath('.//ol/li')[1:]

            for i in range(len(elms)):
                item_info["cat_path_" + str(i)] = elms[i].xpath("./a")[0].attrib["href"]
                item_info["cat_name_" + str(i)] = elms[i].xpath("./a/span")[0].text

            img_elms = html.xpath('//div[@class="productThumb"]/ul/li/a/img')
            for i in range(len(img_elms)):
                item_info["img_url_" + str(i)] ="https:" + img_elms[i].attrib["src"]
            
            try:
                item_info["price_num"] = html.xpath('//p[@class="priceNum"]/span[@class="num"]')[0].text.replace("￥","").replace(",","") if len( html.xpath('//p[@class="priceNum"]/span[@class="num"]')) > 0 else ""
                item_info["price_tax"] = html.xpath('//p[@class="priceNum"]/span[@class="tax"]')[0].text.replace("￥","").replace(",","") if len( html.xpath('//p[@class="priceNum"]/span[@class="tax"]')) > 0 else ""
            except:
                item_info["price_num"] = "-"
                item_info["price_tax"] = "-"

            item_info["item_name"] = html.xpath('//h1[@class="productTitle wrongInformationModalTarget-name"]')[0].text.strip().replace("\u3000"," ")
            item_info["item_format"] =  html.xpath('//span[@class="format"]/span')[0].attrib["content"] if len(html.xpath('//span[@class="format"]/span')) > 0 else ""
            item_info["item_jancode"] =  html.xpath('//span[@class="janCode"]')[0].text.split("：")[1] if len(html.xpath('//span[@class="janCode"]')) > 0 else ""

            item_info["success"] = True
            return item_info

        except Exception as e:
            item_info["error_message"] = f"{e}"
            time.sleep(2)

    else:
        return item_info


if __name__ == "__main__":
    item = get_item_info("5259253")
    print(item)