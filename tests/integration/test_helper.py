import json
import time

import floto
from floto.decider import Decider


def get_result(domain, run_id, workflow_id):
    response = floto.api.Swf().get_workflow_execution_history('floto_test', run_id, workflow_id)
    response['startedEventId'] = 1
    response['previousStartedEventId'] = 1
    history = floto.History('floto_test', 'no_task_list', response)
    wf_completed = history.get_events_by_type('WorkflowExecutionCompleted')[0]
    result = json.loads(history.get_event_attributes(wf_completed)['result'])
    return result


def get_fail_workflow_execution(domain, run_id, workflow_id):
    response = floto.api.Swf().get_workflow_execution_history('floto_test', run_id, workflow_id)
    response['startedEventId'] = 1
    response['previousStartedEventId'] = 1
    history = floto.History('floto_test', 'no_task_list', response)

    failed_event = history.get_events_by_type('WorkflowExecutionFailed')[0]
    details = json.loads(history.get_event_attributes(failed_event)['details'])
    return details


def is_workflow_completed(domain, run_id, workflow_id):
    response = floto.api.Swf().get_workflow_execution_history('floto_test', run_id, workflow_id)
    response['startedEventId'] = 1
    response['previousStartedEventId'] = 1
    history = floto.History('floto_test', 'no_task_list', response)
    result = None
    if history.get_events_by_type('WorkflowExecutionCompleted'):
        wf_completed = history.get_events_by_type('WorkflowExecutionCompleted')[0]
        result = json.loads(history.get_event_attributes(wf_completed)['result'])
    return result


def get_activity_result(result, name, version):
    return [v for (k, v) in result.items() if name + ':' + version in k][0]


class DeciderEarlyExit(Decider):
    def __init__(self, repetitions, **args):
        super().__init__(**args)
        self.executions = 0
        if repetitions:
            self.repetitions = repetitions
        else:
            self.repetitions = 2

    def tear_down(self):
        self.executions += 1
        if self.executions < self.repetitions:
            super().tear_down()
        else:
            self.terminate_decider = True


class SlowDecider(Decider):
    def __init__(self, decider_spec):
        super().__init__(decider_spec=decider_spec)
        self.timed_out = 0
        self.max_timed_out = 1

    def get_decisions(self):
        if self.timed_out < self.max_timed_out:
            time.sleep(5)
            self.timed_out += 1
        super().get_decisions()
