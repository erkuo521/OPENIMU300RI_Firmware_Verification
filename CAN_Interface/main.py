'''
CAN testing script
v3.1.8 20210726 erkuo chen
pls select right app which are tested now
'''

import os
import sys
import time
import json
import traceback
from excel_sheet import my_csv
from device import aceinna_device
from driver import aceinna_driver
from test_case import aceinna_test_case
from gpio import aceinna_gpio

# def main(debug_main = False, dev_type = 'MTLT305D'):
def main(dev_type = 'MTLT305D', app = 'IMU', bcm_pin_list = []): 
    start_time = time.time()   
    loc_time = '_'.join([str(x) for x in list(time.localtime())])
    with open('can_attribute_' + dev_type + '_' + app + '.json') as json_data:
        can_attribute = json.load(json_data)
    debug_main = True if can_attribute['debug_mode'].upper() == 'TRUE' else False
    testitems = can_attribute['test_items'] # testitems = ['3.6']

    gpio_list = []
    bcm_pin_list.sort()
    for pin in bcm_pin_list: # created gpio instance based on pins, sorted the list firstly
        exec(f'gpio_{pin}=aceinna_gpio(pwr_pin = {pin}, use_gpio=True)') # sequence is correspond to sequency indev_nodes.
        exec(f'gpio_list.append(gpio_{pin})')  

    main_driver = aceinna_driver(debug_mode = debug_main)
    dev_nodes = main_driver.get_can_nodes()    

    device_list = []
    for idx,i in enumerate(dev_nodes):
        ad = aceinna_device(i, attribute_json = can_attribute,debug_mode = debug_main, power_gpio=gpio_list[idx], devtype=dev_type, app_type=app)
        main_driver.register_dev(dev_src = i, instance_dev = ad) # regist each device to driver
        ad.add_driver(main_driver)
        ad.update_sn(j1939_format=True)
        device_list.append(ad) # add each device instance to device_list
    if debug_main: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':len(device_list)})

    for i in device_list:
        print('start testing device_src:{0} device_sn:{1}'.format(hex(i.src), hex(i.sn_can)))
        if debug_main: eval('input([k, i, j, m])', {'k':sys._getframe().f_code.co_name,'i':hex(i.sn_can), 'j':hex(i.src), 'm':'press enter:'})
        if  os.path.exists(os.path.join(os.getcwd(), 'data')) == False:
            os.mkdir(os.path.join(os.getcwd(), 'data'))
        test_file = my_csv(os.path.join(os.getcwd(), 'data','CAN-testing_result_{0:#X}_{1:#X}_{2}_FW{3}_{4}.csv'.format(i.src, i.sn_can, dev_type, can_attribute['predefine']['fwnum']+'_'+app, loc_time)))
        main_test = aceinna_test_case(test_file, debug_mode = debug_main)
        main_test.set_test_dev(i, fwnum=int(can_attribute['predefine']['fwnum'], 16))  # need to be updated for each testing ----------input: 1        
        main_test.run_test_case(test_item = testitems, start_idx = can_attribute['start_idx']) # do single/multi items test in testitems list if needed
    print(f'testing finished, {time.time()-start_time} seconds used')
    
    return True

if __name__ == "__main__":
    input('will start main(), press Enter:')
    try:
        print(time.time())
        # main(debug_main = False, dev_type = 'MTLT335')  # open debug mode
        main(dev_type = 'OPENIMU300RI', app='IMU',bcm_pin_list=[4])  # ---- from type in JSON, need to select app type ----
    except Exception as e:
        print(e)
        traceback.print_exc()
  
    