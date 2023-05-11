# Bike counter site information

site_01 = dict(site_url='/annarbor-1',
               site_title='Ann Arbor Division Street Bikeway',
               data_file_name='export_data_domain_7992.xlsx',
               weather_file_name='weather-noaa-annarbor.csv',
               note_file_name='notes-annarbor.csv',
               config_direction={'in': 'Northbound',
                                 'out': 'Southbound'},
               loc_msg_markdown='[Ann Arbor Division Street Bikeway](https://www.a2dda.org/people-friendly-streets/projects/division-street-bikeway-project/) | [Site photo](https://fenggroup.org/images/respic/bike-counter-a2division.png) | [Site location](https://goo.gl/maps/1bcfHrqSYbqiRSXa8)',
               dates_msg='Data collection: 2022: Aug 26 to Nov 19, 2023: May 1 to present',
               date_range=['2022-08-26',   # the first full *day* of data collection
                           '2023-05-07'],
               default_res='1_day',
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
               default_res='1_day',
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
               default_res='1_hour',
              )

site_list = [site_01, site_02, site_03]