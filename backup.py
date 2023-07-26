import boto3
import datetime
from datetime import datetime, timedelta, tzinfo

class Zone(tzinfo):
    def __init__(self,offset,isdst,name):
        self.offset = offset
        self.isdst = isdst
        self.name = name
    def utcoffset(self, dt):
        return timedelta(hours=self.offset) + self.dst(dt)
    def dst(self, dt):
        return timedelta(hours=1) if self.isdst else timedelta(0)
    def tzname(self,dt):
        return self.name

UTC = Zone(10,False,'UTC')

# Setting retention period of 365 days
date_1_year = datetime.now(UTC) - timedelta(days=1)

def lambda_handler(event, context):
    client = boto3.client('rds')
    
    #Delete snapshot
    print("Snapshots to be deleted older than Date - " + str(date_1_year))
    #Connecting to RDS
    rds = boto3.setup_default_session(region_name='ap-south-1')
    
    snapshots = client.describe_db_snapshots(SnapshotType='manual', DBInstanceIdentifier= 'bepwordpress')
    print('Deleting all DB Snapshots older than %s' % date_1_year)

    for i in snapshots['DBSnapshots']:
        print(i['DBSnapshotIdentifier'])
        if i['SnapshotCreateTime'] < date_1_year:
            print ('Deleting snapshot %s' % i['DBSnapshotIdentifier'])
            client.delete_db_snapshot(DBSnapshotIdentifier=i['DBSnapshotIdentifier'])
            
    #Create Snapshot
    now = datetime.now()
    date = now.strftime("%d-%m-%Y-%H-%M-%S")
    tagname = now.strftime("%d-%m-%Y")
    #print("date and time =", date)
    response = client.create_db_snapshot(
    DBSnapshotIdentifier='bepwordpress-auto-{}'.format(date),
    DBInstanceIdentifier='bepwordpress',
    Tags=[
        {
            'Key': 'backupon',
            'Value': tagname
        },
     ]
    )