"""
Sync Script which sync the data with given database
"""
import os
import pymssql
import pandas as pd
import logging
from .api_parser import APIParser


class SyncDB:

    connection = None
    client = None
    NXRATECHARGES = []

    def __init__(self, *args, **kwargs):
        """
        initializes the db connection
        """
        self.DB_HOST = kwargs.get('DB_HOST', os.getenv('DB_HOST', None))
        self.DB_NAME = kwargs.get('DB_NAME', os.getenv('DB_NAME', None))
        self.DB_USER = kwargs.get('DB_USER', os.getenv('DB_USER', None))
        self.DB_PASSWORD = kwargs.get(
            'DB_PASSWORD', os.getenv('DB_PASSWORD', None))
        self.DB_PORT = kwargs.get('DB_PORT', os.getenv('DB_PORT', None))
        self._validate()

    def _validate(self):
        """
        Validates the given parameters
        """
        assert self.DB_HOST is not None, "DB_HOST is required"
        assert self.DB_NAME is not None, "DB_NAME is required"
        assert self.DB_USER is not None, "DB_USER is required"
        assert self.DB_PASSWORD is not None, "DB_PASSWORD is required"
        assert self.DB_PORT is not None, "DB_PORT is required"
        self.api = APIParser()
        self._connect()

    def _connect(self):
        """
        which connects with the databsae
        """
        self.connection = pymssql.connect(
            self.DB_HOST, self.DB_USER, self.DB_PASSWORD, self.DB_NAME)
        self.client = self.connection.cursor()

    def _fetch(self, query):
        """
        internal method to fetch the data and returns dataframe
        """
        df = pd.read_sql(query, self.connection)
        return df

    def get_tarrif_results(self, from_date=None, to_date=None):
        """
        will result the tarrif details from_date to to_date
        """
        self.tarrif_data = self.api.fetch(from_date=from_date, to_date=to_date)
        return self.tarrif_data

    def get_tarrif_types(self):
        """
        will return all the tarrif types
        """
        query = "SELECT * FROM [NXLTariffType]"  # TODO: do we need all columns?
        self.tarrif_types = self._fetch(query)
        return self.tarrif_types

    def get_nxgen_ability_id(self, tarrif_id=None):
        """
        will return the specifid tarrfi id
        """
        query = "SELECT * from NXLGenabilityRateID where G_MasterTariffID = {}".format(
            tarrif_id)  # TODO: might be sql injection prevention required?
        self.ability_id = self._fetch(query)
        return self.ability_id

    def get_calculation_types(self):
        """
        will return the all the calc types
        """
        query = "select * from NXLCalcType"  # TODO: do we need all columns?
        self.calc_types = self._fetch(query)
        return self.calc_types

    def get_time_of_use_of_types(self):
        """
        will return all the time of use of types
        """
        query = "select * from NXLCalcType"  # TODO: do we need all columns?
        self.tou_types = self._fetch(query)
        return self.tou_types

    def compute_RateID(self, tarrif=None):
        """
        will compute the RateID column
        """
        pass

    def compute_UtilityID(self, tarrif=None):
        """
        will compute the UtilityID column
        """
        pass

    def compute_Rate(self, tarrif=None):
        """
        Will compute the Rate column
        """
        pass

    def compute_TariffChargeType(self, tarrif=None):
        """
        Will compute the Rate column
        """
        pass

    def compute_CalcType(self, tarrif=None):
        """
        will compute the tarrif calc type
        """
        calc_type = self.calc_types.loc[self.calc_types['ChargeType']
                                        == tarrif['ChargeType']]
        # TODO: Identify the specific field

    def compute_TOU(self, tarrif=None):
        """
        Will compute the TOU column
        """
        pass

    def compute_LimitStart(self, tarrif=None):
        """
        Will compute the LimitStart column
        """
        pass

    def compute_LimitEnd(self, tarrif=None):
        """
        Will compute the LimitEnd column
        """
        pass

    def compute_Charges(self, tarrif=None):
        """
        Will compute the Charges column
        """
        pass

    def compute_Notes(self, tarrif=None):
        """
        Will compute the Notes column
        """
        pass

    def compute_CreatedOn(self, tarrif=None):
        """
        Will compute the CreatedOn column
        """
        pass

    def compute_CreatedBy(self, tarrif=None):
        """
        Will compute the CreatedBy column
        """
        pass

    def compute_Version(self, tarrif=None):
        """
        Will compute the Version column
        """
        pass

    def run(self):
        """
        Core method to start the process
        """
        # 1. Get the tarrif details
        self.get_tarrif_results()
        # 2. Get tarrif types
        self.get_tarrif_types()
        # 3. Get calc types
        self.get_calculation_types()
        # 4. Get TOU types
        self.get_time_of_use_of_types()
        # 5. For each tarrif, prepare payload (which consists the rate changes/tarrif)
        # This is where calculation needs to be done
        for tarrif in self.tarrif_data:
            tarrif_df = self.get_nxgen_ability_id(tarrif.get('tariffId'))
            # 6. Insert payload into another table
            for rate in tarrif.get('rates', []):
                payload = {
                    'RateID': None,
                    'UtilityID': None,
                    'ActiveDateFrom': None,
                    'ActiveDateTo': None,
                    'Rate': None,
                    'TariffChargeType': None,
                    'CalcType': None,
                    'TOU': None,
                    'LimitStart': None,
                    'LimitEnd': None,
                    'Charges': None,
                    'Notes': None,
                    'CreatedOn': None,
                    'CreatedBy': None,
                    'Version': None
                }
                # Calculate the payload
                self.persist_NXRATECHARGES(payload)

    def persist_NXRATECHARGES(self, payload=dict):
        """
        will add entry in `NXRATECHARGES` (Local persistance)
        """
        self.NXRATECHARGES.append(payload)

    def save_NXRATECHARGES(self):
        """
        saves the persisted records into table `NXRATECHARGES`
        """
        columns = ', '.join(self.NXRATECHARGES[0].keys())
        values = [tuple(payload.values()) for payload in self.NXRATECHARGES]
        query = "INSERT INTO {tablename} ({columns}) VALUES ($d, $d, $s, $s, $s, $s, $s, $s, $s, $s, $s, $s, $s, $s, $s);" .format(
            tablename='NXRATECHARGES',
            columns=columns
        )
        try:
            self.client.executemany(query, values)
            self.client.commit()
        except Exception as e:
            logging.error("Data saving failed")
            logging.error("TraceBack: {}".format(str(e)))
            raise ValueError("Invalid data")
            return False
        finally:
            self._close()
        return True

    def _close(self):
        """
        which closes the db connection
        """
        self.connection.close()


sync = SyncDB(
    DB_HOST='aei-az-sqldev.nxe.nxegen.com',
    DB_NAME='rtisdevel',
    DB_USER='nordic067',
    DB_PASSWORD='RTIS_Development'
)
sync.run()
