# 3 Fasen



WARN     mqttclient need to start mqqt client                                                                                                         
INFO     mqttclient create mqtt client 192.168.1.99                                                                                                   
connecting to mqtt server 192.168.1.99                                                                                                                
Connected                                                                                                                                             
INFO     p1meter    listening on UART for P1 meter data                                                                                               
DEBUG    main       freed: 259.584 - now free: 4.050.064                                                                                              
DEBUG    p1meter    footer found                                                                                                                      
DEBUG    p1meter    RX computed CRC 1392                                                                                                              
DEBUG    p1meter    {'unit': 'A', 'meter': '1-0:51.7.0', 'reading': '000'}                                                                            
DEBUG    p1meter    {'unit': None, 'meter': '1-0:52.32.0', 'reading': '00000'}                                                                        
DEBUG    p1meter    {'unit': None, 'meter': '1-0:32.36.0', 'reading': '00000'}                                                                        
DEBUG    p1meter    {'unit': None, 'meter': '1-0:32.32.0', 'reading': '00001'}                                                                        
DEBUG    p1meter    {'unit': 'kWh', 'meter': '1-0:1.8.2', 'reading': '000000.011'}                                                                    
DEBUG    p1meter    {'unit': None, 'meter': '0-0:96.7.21', 'reading': '00001'}                                                                        
DEBUG    p1meter    {'unit': None, 'meter': '1-0:72.32.0', 'reading': '00001'}                                                                        
DEBUG    p1meter    {'unit': 'kW', 'meter': '1-0:41.7.0', 'reading': '00.000'}                                                                        
DEBUG    p1meter    {'unit': 'kW', 'meter': '1-0:61.7.0', 'reading': '00.000'}                                                                        
DEBUG    p1meter    {'unit': 'kW', 'meter': '1-0:42.7.0', 'reading': '00.000'}                                                                        
DEBUG    p1meter    {'unit': 'kW', 'meter': '1-0:62.7.0', 'reading': '00.000'}                                                                        
DEBUG    p1meter    {'unit': 'kW', 'meter': '1-0:22.7.0', 'reading': '01.966'}                                                                        
DEBUG    p1meter    {'unit': None, 'meter': '0-1:24.1.0', 'reading': '003'}                                                                           
DEBUG    p1meter    {'unit': None, 'meter': '0-1:96.1.0', 'reading': '00'}                                                                            
DEBUG    p1meter    {'unit': None, 'meter': '1-3:0.2.8', 'reading': '50'}                                                                             
DEBUG    p1meter    {'unit': 'V', 'meter': '1-0:32.7.0', 'reading': '233.5'}                                                                          
DEBUG    p1meter    {'unit': None, 'meter': '1-0:99.97.0', 'reading': '0-0:96.7.19'}                                                                  
DEBUG    p1meter    {'unit': 'kWh', 'meter': '1-0:2.8.2', 'reading': '000001.136'}                                                                    
DEBUG    p1meter    {'unit': 'A', 'meter': '1-0:31.7.0', 'reading': '008'}                                                                            
DEBUG    p1meter    {'unit': None, 'meter': '0-0:96.14.0', 'reading': '0002'}                                                                         
DEBUG    p1meter    {'unit': None, 'meter': '0-0:1.0.0', 'reading': '210223135742W'}                                                                  
DEBUG    p1meter    {'unit': 'A', 'meter': '1-0:71.7.0', 'reading': '000'}                                                                            
DEBUG    p1meter    {'unit': 'kWh', 'meter': '1-0:1.8.1', 'reading': '000000.000'}                                                                    
DEBUG    p1meter    {'unit': None, 'meter': '0-0:96.13.0', 'reading': ''}                                                                             
DEBUG    p1meter    {'unit': None, 'meter': '1-0:72.36.0', 'reading': '00000'}                                                                        
DEBUG    p1meter    {'unit': 'kW', 'meter': '1-0:1.7.0', 'reading': '00.000'}                                                                         
DEBUG    p1meter    {'unit': 'kW', 'meter': '1-0:21.7.0', 'reading': '00.000'}                                                                        
DEBUG    p1meter    {'unit': None, 'meter': '1-0:52.36.0', 'reading': '00000'}                                                                        
DEBUG    p1meter    {'unit': None, 'meter': '0-0:96.1.1', 'reading': '4530303630313030303033323436363230'}    
DEBUG    p1meter    {'unit': 'kWh', 'meter': '1-0:2.8.1', 'reading': '000000.000'}                                                                    
DEBUG    p1meter    {'unit': None, 'meter': '0-0:96.7.9', 'reading': '00000'}                                                                         
DEBUG    p1meter    {'unit': 'V', 'meter': '1-0:52.7.0', 'reading': '232.7'}                                                                          
DEBUG    p1meter    {'unit': 'V', 'meter': '1-0:72.7.0', 'reading': '234.0'}                                                                          
DEBUG    p1meter    {'unit': 'kW', 'meter': '1-0:2.7.0', 'reading': '01.966'}                                                                         
DEBUG    p1meter    1-0:51.7.0.* --> instant/current/l2_A                                                                                             
DEBUG    p1meter    1-0:52.32.0 --> outages/voltage_sags/l2                                                                                           
DEBUG    p1meter    1-0:32.36.0 --> outages/short_power_peaks                                                                                         
DEBUG    p1meter    1-0:32.32.0 --> outages/short_power_drops                                                                                         
DEBUG    p1meter    1-0:1.8.2 --> total/consumption_high_tariff_kWh                                                                                   
DEBUG    p1meter    0-0:96.7.21 --> outages/short_power_outages                                                                                       
DEBUG    p1meter    1-0:72.32.0 --> outages/voltage_sags/l3                                                                                           
DEBUG    p1meter    1-0:41.7.0 --> instant/power_consumption/l2_kW                                                                                    
DEBUG    p1meter    1-0:61.7.0 --> instant/power_consumption/l3_kW                                                                                    
DEBUG    p1meter    1-0:42.7.0.* --> instant/power_production/l2_kW                                                                                   
DEBUG    p1meter    1-0:62.7.0.* --> instant/power_production/l3_kW                                                                                   
DEBUG    p1meter    1-0:22.7.0.* --> instant/power_production/l1_kW                                                                                   
DEBUG    p1meter    0-(\d):24.1.0 --> equipment/devicetype_id_1                                                                                       
DEBUG    p1meter    0-1:96.1.0.* --> equipment/p1_meter_id                                                                                            
DEBUG    p1meter    1-3:0.2.8.* --> equipment/version                                                                                                 
DEBUG    p1meter    1-0:32.7.0 --> instant/voltage/l1_V                                                                                               
DEBUG    p1meter    1-0:99.97.0 --> outages/power_failure_event_log                                                                                   
DEBUG    p1meter    1-0:2.8.2 --> total/production_high_tariff_kWh                                                                                    
DEBUG    p1meter    1-0:31.7.0.* --> instant/current/l1_A                                                                                             
DEBUG    p1meter    0-0:96.14.0.* --> tariff_indicator                                                                                                
DEBUG    p1meter    0-0:1.0.0.* --> date_time                                                                                                         
DEBUG    p1meter    1-0:71.7.0.* --> instant/current/l3_A                                                                                             
DEBUG    p1meter    1-0:1.8.1 --> total/consumption_low_tariff_kWh                                                                                    
DEBUG    p1meter    0-0:96.13.(\d) --> message/0                                                                                                      
DEBUG    p1meter    1-0:72.36.0 --> outages/voltage_swells/l3                                                                                         
DEBUG    p1meter    1-0:1.7.0.* --> instant/consumption_kW                                                                                            
DEBUG    p1meter    1-0:21.7.0 --> instant/power_consumption/l1_kW                                                                                    
DEBUG    p1meter    1-0:52.36.0 --> outages/voltage_swells/l2                                                                                         
DEBUG    p1meter    0-(\d):96.1.1.* --> equipment/m-bus_0_id                                                                                          
DEBUG    p1meter    1-0:2.8.1 --> total/production_low_tariff_kWh                                                                                     
DEBUG    p1meter    0-0:96.7.9 --> outages/long_power_outages                                                                                         
DEBUG    p1meter    1-0:52.7.0 --> instant/voltage/l2_V                                                                                               
DEBUG    p1meter    1-0:72.7.0 --> instant/voltage/l3_V                                                                                               
DEBUG    p1meter    1-0:2.7.0.* --> instant/production_kW                                                                                             
DEBUG    p1meter    readings: [{'unit': 'A', 'meter': 'instant/current/l2_A', 'reading': '000'}, {'unit': None, 'meter': 'outages/voltage_sags/l2', 'r
eading': '00000'}, {'unit': None, 'meter': 'outages/short_power_peaks', 'reading': '00000'}, {'unit': None, 'meter': 'outages/short_power_drops', 'rea
ding': '00001'}, {'unit': 'kWh', 'meter': 'total/consumption_high_tariff_kWh', 'reading': '000000.011'}, {'unit': None, 'meter': 'outages/short_power_
outages', 'reading': '00001'}, {'unit': None, 'meter': 'outages/voltage_sags/l3', 'reading': '00001'}, {'unit': 'kW', 'meter': 'instant/power_consumpt
ion/l2_kW', 'reading': '00.000'}, {'unit': 'kW', 'meter': 'instant/power_consumption/l3_kW', 'reading': '00.000'}, {'unit': 'kW', 'meter': 'instant/po
wer_production/l2_kW', 'reading': '00.000'}, {'unit': 'kW', 'meter': 'instant/power_production/l3_kW', 'reading': '00.000'}, {'unit': 'kW', 'meter': '
instant/power_production/l1_kW', 'reading': '01.966'}, {'unit': None, 'meter': 'equipment/devicetype_id_1', 'reading': '003'}, {'unit': None, 'meter':
 'equipment/p1_meter_id', 'reading': '00'}, {'unit': None, 'meter': 'equipment/version', 'reading': '50'}, {'unit': 'V', 'meter': 'instant/voltage/l1_
V', 'reading': '233.5'}, {'unit': None, 'meter': 'outages/power_failure_event_log', 'reading': '0-0:96.7.19'}, {'unit': 'kWh', 'meter': 'total/product
ion_high_tariff_kWh', 'reading': '000001.136'}, {'unit': 'A', 'meter': 'instant/current/l1_A', 'reading': '008'}, {'unit': None, 'meter': 'tariff_indi
cator', 'reading': '0002'}, {'unit': None, 'meter': 'date_time', 'reading': '210223135742W'}, {'unit': 'A', 'meter': 'instant/current/l3_A', 'reading'
: '000'}, {'unit': 'kWh', 'meter': 'total/consumption_low_tariff_kWh', 'reading': '000000.000'}, {'unit': None, 'meter': 'message/0', 'reading': ''}, 
{'unit': None, 'meter': 'outages/voltage_swells/l3', 'reading': '00000'}, {'unit': 'kW', 'meter': 'instant/consumption_kW', 'reading': '00.000'}, {'un
it': 'kW', 'meter': 'instant/power_consumption/l1_kW', 'reading': '00.000'}, {'unit': None, 'meter': 'outages/voltage_swells/l2', 'reading': '00000'},
 {'unit': None, 'meter': 'equipment/m-bus_0_id', 'reading': '4530303630313030303033323436363230'}, {'unit': 'kWh', 'meter': 'total/production_low_tari
ff_kWh', 'reading': '000000.000'}, {'unit': None, 'meter': 'outages/long_power_outages', 'reading': '00000'}, {'unit': 'V', 'meter': 'instant/voltage/
l2_V', 'reading': '232.7'}, {'unit': 'V', 'meter': 'instant/voltage/l3_V', 'reading': '234.0'}, {'unit': 'kW', 'meter': 'instant/production_kW', 'read
ing': '01.966'}]                                                                                                                                      
