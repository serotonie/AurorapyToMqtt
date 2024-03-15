from dotenv import load_dotenv
import os
from aurorapy.client import AuroraError, AuroraTCPClient
import time

load_dotenv()

def PowerOne(SunUp):

    c = AuroraTCPClient(ip=os.getenv('AURORA_POWERONE_HOST'), port=int(os.getenv('AURORA_POWERONE_PORT')), address=int(os.getenv('AURORA_POWERONE_ADRESSE')))

    try:

        c.connect()
        result = dict()

        result["product_number"] = c.pn()

        result["serial_number"] = c.serial_number()

        if SunUp:
            output_power = c.measure(3)
            input_voltage = c.measure(23)
            input1_current = c.measure(25)
            input2_current = c.measure(27)
            inverter_temperature = c.measure(21)
        else:
            output_power = 0.0
            input_voltage = 0.0
            input1_current = 0.0
            input2_current = 0.0
            inverter_temperature = 0.0

        result["output_power"] = output_power 
        result["input_voltage"] = input_voltage
        result["input1_current"] = input1_current 
        result["input2_current"] = input2_current
        result["ampsTot"] = input1_current + input2_current
        result["inverter_temperature"] = inverter_temperature

        #ENERGY DAILY
        result["daily_energy"] = c.cumulated_energy(period=0) / 1000

        #ENERGY WEEK
        result["energy_week"] = c.cumulated_energy(period=1) / 1000

        #ENERGY MONTH
        result["energy_month"] = c.cumulated_energy(period=3) / 1000

        #ENERGY YEAR
        result["year_energy"] = c.cumulated_energy(period=4) / 1000

        #ENERGY TOTAL
        result["energy_total"] = c.cumulated_energy(period=5) / 1000

        return result

        c.close()

    except Exception as e:
        if str(e) == 'Unknown transmission state':
            print(str(e) + ' - the light is probably to low')
            time.sleep(60)
        else:
            print(e)
