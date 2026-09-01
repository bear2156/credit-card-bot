"""
Web Scraper Module - أتمتة إدخال البيانات على المواقع
تم إنشاء نسخة محسّنة مع معالجة الأخطاء
"""

import time
import logging
from typing import Dict, Optional
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import Select
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.warning("Selenium غير متاح - بعض الميزات قد لا تعمل")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebScraper:
    """فئة لأتمتة إدخال البيانات على المواقع"""

    def __init__(self, headless: bool = False):
        """
        تهيئة السكريبتر
        
        Args:
            headless: تشغيل المتصفح بدون واجهة رسومية
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium غير متاح. يرجى تثبيت: pip install selenium")
        
        self.headless = headless
        self.driver = None
        self.results = []
        self.session_start = datetime.now()
        self.driver_initialized = False

    def initialize_driver(self) -> bool:
        """تهيئة متصفح Chrome"""
        try:
            options = webdriver.ChromeOptions()
            
            if self.headless:
                options.add_argument('--headless')
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--start-maximized')

            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(30)
            self.driver.set_script_timeout(30)
            self.driver_initialized = True
            logger.info("تم تهيئة المتصفح بنجاح")
            return True

        except WebDriverException as e:
            logger.error(f"خطأ في تهيئة المتصفح: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"خطأ غير متوقع في تهيئة المتصفح: {str(e)}")
            return False

    def fill_card_form(self, url: str, card_data: Dict, selectors: Dict) -> dict:
        """
        ملء نموذج البطاقة على موقع معين
        
        Args:
            url: رابط الموقع
            card_data: بيانات البطاقة
            selectors: CSS selectors للحقول
                
        Returns:
            dict: نتيجة العملية
        """
        result = {
            'url': url,
            'website': card_data.get('website', 'unknown'),
            'status': 'failed',
            'message': '',
            'timestamp': datetime.now().isoformat(),
            'duration': 0
        }

        if not self.driver_initialized or self.driver is None:
            result['message'] = 'المتصفح غير مهيأ'
            self.results.append(result)
            return result

        start_time = time.time()

        try:
            logger.info(f"جاري فتح الموقع: {url}")
            self.driver.get(url)
            time.sleep(2)

            # ملء حقل رقم البطاقة
            if selectors.get('card_number'):
                try:
                    card_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selectors['card_number']))
                    )
                    card_input.clear()
                    card_input.send_keys(card_data.get('card_number', ''))
                    time.sleep(0.5)
                    logger.info("تم ملء رقم البطاقة")
                except TimeoutException:
                    logger.warning(f"لم يتم العثور على حقل رقم البطاقة: {selectors['card_number']}")

            # ملء اسم حامل البطاقة
            if selectors.get('cardholder') and card_data.get('cardholder_name'):
                try:
                    name_input = self.driver.find_element(By.CSS_SELECTOR, selectors['cardholder'])
                    name_input.clear()
                    name_input.send_keys(card_data['cardholder_name'])
                    time.sleep(0.5)
                    logger.info("تم ملء اسم حامل البطاقة")
                except NoSuchElementException:
                    logger.warning(f"لم يتم العثور على حقل الاسم: {selectors['cardholder']}")

            # ملء الشهر
            if selectors.get('month'):
                try:
                    month_element = self.driver.find_element(By.CSS_SELECTOR, selectors['month'])
                    if month_element.tag_name == 'select':
                        month_select = Select(month_element)
                        month_select.select_by_value(card_data.get('month', ''))
                    else:
                        month_element.clear()
                        month_element.send_keys(card_data.get('month', ''))
                    time.sleep(0.5)
                    logger.info("تم ملء الشهر")
                except Exception as e:
                    logger.warning(f"خطأ في ملء الشهر: {str(e)}")

            # ملء السنة
            if selectors.get('year'):
                try:
                    year_element = self.driver.find_element(By.CSS_SELECTOR, selectors['year'])
                    if year_element.tag_name == 'select':
                        year_select = Select(year_element)
                        year_select.select_by_value(card_data.get('year', ''))
                    else:
                        year_element.clear()
                        year_element.send_keys(card_data.get('year', ''))
                    time.sleep(0.5)
                    logger.info("تم ملء السنة")
                except Exception as e:
                    logger.warning(f"خطأ في ملء السنة: {str(e)}")

            # ملء CVV
            if selectors.get('cvv'):
                try:
                    cvv_input = self.driver.find_element(By.CSS_SELECTOR, selectors['cvv'])
                    cvv_input.clear()
                    cvv_input.send_keys(card_data.get('cvv', ''))
                    time.sleep(0.5)
                    logger.info("تم ملء CVV")
                except NoSuchElementException:
                    logger.warning(f"لم يتم العثور على حقل CVV: {selectors['cvv']}")

            # الضغط على زر الإرسال
            if selectors.get('submit'):
                try:
                    submit_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selectors['submit']))
                    )
                    submit_btn.click()
                    time.sleep(3)
                    logger.info("تم الضغط على زر الإرسال")

                    result['status'] = 'success'
                    result['message'] = 'تم إدخال البيانات بنجاح'
                except TimeoutException:
                    result['message'] = 'انتهت المهلة الزمنية - لم يتم العثور على زر الإرسال'
                except Exception as e:
                    result['message'] = f'خطأ في الضغط على الزر: {str(e)}'
            else:
                result['status'] = 'partial'
                result['message'] = 'تم ملء البيانات لكن لم يتم الضغط على الزر'

        except TimeoutException as e:
            result['message'] = f'انتهت المهلة الزمنية - الموقع لم يستجب: {str(e)}'
            logger.error(f"TimeoutException: {str(e)}")
        except NoSuchElementException as e:
            result['message'] = f'لم يتم العثور على العنصر: {str(e)}'
            logger.error(f"NoSuchElementException: {str(e)}")
        except WebDriverException as e:
            result['message'] = f'خطأ في المتصفح: {str(e)}'
            logger.error(f"WebDriverException: {str(e)}")
        except Exception as e:
            result['message'] = f'حدث خطأ: {str(e)}'
            logger.error(f"Exception: {str(e)}")

        result['duration'] = time.time() - start_time
        self.results.append(result)
        return result

    def close(self):
        """إغلاق المتصفح"""
        if self.driver_initialized and self.driver is not None:
            try:
                self.driver.quit()
                self.driver_initialized = False
                logger.info("تم إغلاق المتصفح بنجاح")
            except Exception as e:
                logger.warning(f"خطأ في إغلاق المتصفح: {str(e)}")
