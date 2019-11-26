from prometheus_client import CollectorRegistry, Gauge, Counter, push_to_gateway
import asyncio

registry = CollectorRegistry()
gateway = "localhost:9092"
job = "air_quality_production"
g = Gauge('job_last_success_unixtime',
          'Last time a job successfully finished', registry=registry)
start_time = Gauge('job_start_unixtime',
          'Bluesense start time', registry=registry)

p25 = Gauge('pm25', 'PM2.5 data ug/m^3', registry=registry)
p10 = Gauge('pm10', 'PM10 data ug/m^3', registry=registry)
points = Counter('collected_points', 'Update count', registry=registry)
ble_packet_event = Counter('ble_packet_event', "BLE packet received" , registry=registry)
serialpb_packet_event = Counter('serialpb_packet_event', "serialpb buffer protocol packet received" , registry=registry)
channel_serial_error_event = Counter('channel_serial_error_event', "Serial connection packet errors", registry=registry)
channel_serial_packet_event = Counter('channel_serial_packet_event', "Serial connection bytes received", registry=registry)
temp = Gauge('temp', 'Temperature', registry=registry)
hum = Gauge('hum', 'Humidity', registry=registry)
pa = Gauge('pa', 'Pressure', registry=registry)
channel_pb_packet_event = Counter('channel_protobuf_packet_event', "Protobuf connection packet received", registry=registry)
channel_pb_error_event = Counter('channel_protobuf_error_event', "Protobuf connection packet errors", registry=registry)

start_time.set_to_current_time()
push_to_gateway(gateway, job=job, registry=registry)

def update_data():
    g.set_to_current_time()
    points.inc()
    push_to_gateway(gateway, job=job, registry=registry)

async def buffer_queue_stat(rx: asyncio.Queue, tx: asyncio.Queue, data):
    while True:
        buf = await rx.get()
        await tx.put(buf)
        if buf is None:  
            return
        data.inc()
        update_data()
        rx.task_done()
