from prometheus_client import CollectorRegistry, Gauge, Counter, push_to_gateway

registry = CollectorRegistry()
gateway = "localhost:9092"
job = "air_quality_production"
g = Gauge('job_last_success_unixtime',
          'Last time a batch job successfully finished', registry=registry)
p25 = Gauge('pm25', 'pm2.5 data ug/m^3', registry=registry)
p10 = Gauge('pm10', 'pm10 data ug/m^3', registry=registry)
points = Counter('collected_points', 'Collected data points', registry=registry)
serial_error_event = Counter('serial_error_event', "Error events for serial connection", registry=registry)
serial_packet_event = Counter('serial_packet_event', "Packets for serial connection", registry=registry)

def update_data():
    g.set_to_current_time()
    points.inc()
    push_to_gateway(gateway, job=job, registry=registry)
