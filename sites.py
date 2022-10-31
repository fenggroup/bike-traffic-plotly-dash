# Bike counter site information

site_01 = dict(site_url='/annarbor',
                site_title='Ann Arbor N Division protected bike lane',
                  data_file_name='export_data_domain_7992.xlsx',
                  weather_file_name='weather-noaa-annarbor.csv',
                  note_file_name='notes-annarbor.csv',
                  config_direction={'in': 'Northbound',
                                    'out': 'Southbound'},
                  loc_msg_markdown='Location: N Division, Ann Arbor, MI ([Site photo](https://fenggroup.org/images/respic/bike-counter-a2division.png), [Google Maps](https://goo.gl/maps/1bcfHrqSYbqiRSXa8))',
                  dates_msg='Data collection: 2022-08-26 to 2022-10-28 (ongoing)',
                  date_range=['2022-08-26',   # the first full *day* of data collection
                              '2022-10-28'],
                  )

site_02 = dict(site_url='/dearborn-1',
                site_title='Dearborn Rouge Getaway Trail (2022-06-15 to 2022-07-19)',
                  data_file_name='bike_data_dearborn.xlsx',
                  weather_file_name='weather-noaa-dearborn.csv',
                  note_file_name='notes-dearborn.csv',
                  config_direction={'in': 'Eastbound',
                                    'out': 'Westbound'},
                  loc_msg_markdown='Location: Rouge Gateway Trail, Dearborn, MI (Site photo, [Google Maps](https://goo.gl/maps/WzSvLWxtkyoro9oK8))',
                  dates_msg='Data collection: 5 weeks (2022-06-15 to 2022-07-19)',
                  date_range=['2022-06-15',    # the first full *day* of data collection
                              '2022-07-19'],
                  )

site_03 = dict(site_url='/dearborn-2',
                site_title='Dearborn Rouge Getaway Trail (2022-10-08 to 2022-10-29)',
                  data_file_name='bike_dearborn_counter.xlsx',
                  weather_file_name='weather-noaa-dearborn.csv',
                  note_file_name='notes-dearborn.csv',
                  config_direction={'in': 'Eastbound',
                                    'out': 'Westbound'},
                  loc_msg_markdown='Location: Rouge Gateway Trail, Dearborn, MI (Site photo, [Google Maps](https://goo.gl/maps/pBYh8FBJJ9cSNj9S8))',
                  dates_msg='Data collection: 2022-10-08 to 2022-10-27 (ongoing)',
                  date_range=['2022-10-08',    # the first full *day* of data collection
                              '2022-10-11'],
                  )

site_list = [site_01, site_02, site_03]