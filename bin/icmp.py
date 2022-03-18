import os
import sys
import json
import csv
import time
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.modularinput import *
from icmplib.ping import async_ping
from icmplib import ICMPLibError

class Input(Script):
    MASK = "<encrypted>"
    APP = "TA-icmp"

    def get_scheme(self):

        scheme = Scheme("ICMP")
        scheme.description = ("A high performance ICMP input")
        scheme.use_external_validation = False
        scheme.streaming_mode_xml = True
        scheme.use_single_instance = False

        scheme.add_argument(Argument(
            name="file",
            title="Host List File",
            data_type=Argument.data_type_string,
            required_on_create=True,
            required_on_edit=False
        ))
        scheme.add_argument(Argument(
            name="concurrency",
            title="Concurrency Limit",
            data_type=Argument.data_type_number,
            required_on_create=True,
            required_on_edit=False
        ))
        scheme.add_argument(Argument(
            name="count",
            title="Count",
            data_type=Argument.data_type_number,
            required_on_create=True,
            required_on_edit=False
        ))
        scheme.add_argument(Argument(
            name="timeout",
            title="Timeout",
            data_type=Argument.data_type_number,
            required_on_create=True,
            required_on_edit=False
        ))
        return scheme

    def stream_events(self, inputs, ew):
        self.service.namespace['app'] = self.APP
        # Get Variables
        input_name, input_items = inputs.inputs.popitem()
        kind, name = input_name.split("://")
        COUNT = int(input_items['count'])
        CONCURRENCY = int(input_items['concurrency'])
        TIMEOUT = int(input_items['timeout'])

        # Format Target List
        targets = []
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..",input_items['file']), newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for target in reader:
                if target.get('enabled') == "1":
                    targets.append([target['target'],target['asset']])

        ew.log(EventWriter.INFO,f"Pinging {len(targets)} targets {COUNT} times each with a concurrency of {CONCURRENCY} and timeout of {TIMEOUT}")
        start = time.perf_counter()

        asyncio.run(self.splunk_multiping(targets, COUNT,TIMEOUT,CONCURRENCY,ew, input_items['sourcetype'])) #results = multiping(targets,count=COUNT,timeout=TIMEOUT,concurrent_tasks=CONCURRENCY,privileged=False)
        
        stop = time.perf_counter()
        ew.log(EventWriter.INFO,f"Completed in {format(stop-start,'.3f')}s")

    async def splunk_multiping(self, targets, count, timeout, concurrent_tasks, ew, sourcetype):
        loop = asyncio.get_running_loop()
        tasks_pending = set()

        for [address,asset] in targets:
            if len(tasks_pending) >= concurrent_tasks:
                _, tasks_pending = await asyncio.wait(tasks_pending,return_when=asyncio.FIRST_COMPLETED)

            task = loop.create_task(self.ping_print(address, asset, count, timeout, ew, sourcetype))
            tasks_pending.add(task)

        await asyncio.wait(tasks_pending)

    async def ping_print(self, address, asset, count, timeout, ew, sourcetype):
        try:
            result = await async_ping(address=address,count=count,timeout=timeout,privileged=True)
            source = result.address
            if(sourcetype == "icmp:metric"):
                data = f"{asset}:{result.packets_received}/{result.packets_sent}:{format(result.min_rtt, '.3f')}:{format(result.avg_rtt, '.3f')}:{format(result.max_rtt, '.3f')}"
            else:
                data = f"{asset}:{result.packets_received}/{result.packets_sent}:{','.join(format(r, '.3f') for r in result.rtts)}"
        except ICMPLibError as e:
            source = e.__class__.__name__
            ew.log(EventWriter.ERROR,f"TA-icmp address=\"{address}\" asset=\"{asset}\" error=\"{e.__class__.__name__}\" message=\"{e}\"")
            data = f"{asset}:0/0"
        except Exception as e:
            ew.log(EventWriter.ERROR,f"TA-icmp address=\"{address}\" asset=\"{asset}\" error=\"{e.__class__.__name__}\" message=\"{e}\"")
        ew.write_event(Event(
            data=data,
            source=source,
        ))

if __name__ == '__main__':
    exitcode = Input().run(sys.argv)
    sys.exit(exitcode)