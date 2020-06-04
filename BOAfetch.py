from selenium import webdriver
import BOAaccount
import pandas as pd
import time
import driver_setting

"""
driver_setting.py
PATH = "/Users/.../chromedriver" # location of the chrome driver

BOAacccount.py
boa_online_id = ... # online id for login
boa_passward = ... # passcode for login
boa_account = ... # the account for scraping
"""

class AutoAccountBookBOA():
    def __init__(self):
        self.driver = webdriver.Chrome(driver_setting.PATH)
        self.driver.get('https://www.bankofamerica.com/')
        self.trans_date_list = []
        self.trans_desc_list = []
        self.trans_type_list = []
        self.trans_amount_list = []
        self._sign_in()
        self._scrap_web(mode='full')
        self.driver.quit()
        self._data_arrange()

    def _sign_in(self):
        """
        sign in to the Bank of America and get target account
        """
        online_id_input = self.driver.find_element_by_id('onlineId1')
        online_id_input.send_keys(BOAaccount.boa_online_id)
        passcode_input = self.driver.find_element_by_id('passcode1')
        passcode_input.send_keys(BOAaccount.boa_passward)
        sign_in = self.driver.find_element_by_id('signIn')
        sign_in.click()
        time.sleep(5)
        accounts = self.driver.find_elements_by_css_selector('.AccountName > a')
        for account in accounts:
            if account.text == BOAaccount.boa_account:
                print('Account found...')
                account.click()
                break

    def _scrap_web(self, mode='current'):
        """
        mode: current mode will only get information from current cycle,
              full mode will fetch all the information from all cycles
        """
        print('Start fetching information...')
        FLAG = True
        while FLAG:
            try:
                for row in ['even', 'odd']:
                    for each_trans in self.driver.find_elements_by_class_name(row):
                        trans_date = each_trans.find_element_by_class_name('trans-date-cell').text
                        if trans_date != 'Pending':
                            self.trans_date_list.append(trans_date)
                            self.trans_desc_list.append(each_trans.find_element_by_class_name('trans-desc-cell').text)
                            self.trans_amount_list.append(
                                each_trans.find_element_by_class_name('trans-amount-cell').text)
                            trans_type = each_trans.find_element_by_class_name('icon-type-image')
                            trans_type = trans_type.get_attribute("class").split(' ')[1].split('-')[2:]
                            self.trans_type_list.append(' '.join(trans_type))
                if mode == 'current':
                    FLAG = False
                    break
                prev_trans = self.driver.find_element_by_name('goto_previous_transactions_top')
                prev_trans.click()
            except:
                FLAG = False

    # get the dataframe for your account
    def _data_arrange(self):
        """
        get the dataframe for your account, export a csv file.
        """
        if (len(self.trans_date_list) != 0):
            df = pd.DataFrame(self.trans_date_list, columns=['Date'])
            df['Desc'] = self.trans_desc_list
            df['Type'] = self.trans_type_list
            df['Amount'] = self.trans_amount_list
            # remove '$' sign
            df['Amount'] = df.apply(lambda x: ''.join(x['Amount'].split('$')), axis=1)
            # remove ',' sign
            df['Amount'] = df.apply(lambda x: float(''.join(x['Amount'].split(','))), axis=1)
            df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
            df = df.sort_values(by='Date', ascending=False)
            df = df.reset_index(drop=True)
            self.df = df
            df.to_csv('AutoAccountBookBOA.csv', index=False)
            print('Done')
        else:
            print('No data export.')

if __name__ == "__main__":
    account = AutoAccountBookBOA()

