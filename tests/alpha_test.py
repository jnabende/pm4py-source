from pm4py.objects.log.importer.csv import factory as csv_importer
from pm4py.objects.log.importer.xes import factory as xes_importer
import pm4py.objects.log.transform as log_transform
from pm4py.algo.discovery.alpha import factory as alpha_factory
from pm4py.visualization.petrinet.common import visualize as pn_viz
from pm4py.algo.conformance.tokenreplay.versions import token_replay
from pm4py.algo.conformance.tokenreplay.versions.token_replay import NoConceptNameException
from pm4py.objects import petri
from pm4py.objects.petri.exporter import pnml as petri_exporter
from tests.constants import INPUT_DATA_DIR, OUTPUT_DATA_DIR, PROBLEMATIC_XES_DIR
import logging
import unittest
import os

class AlphaMinerTest(unittest.TestCase):
    def obtainPetriNetThroughAlphaMiner(self, log_name):
        if ".xes" in log_name:
            trace_log = xes_importer.import_log(log_name)
        else:
            event_log = csv_importer.import_log(log_name)
            trace_log = log_transform.transform_event_log_to_trace_log(event_log)
        net, marking, fmarking = alpha_factory.apply(trace_log)
        return trace_log, net, marking, fmarking

    def test_applyAlphaMinerToXES(self):
        # calculate and compare Petri nets obtained on the same log to verify that instances
        # are working correctly
        log1, net1, marking1, fmarking1 = self.obtainPetriNetThroughAlphaMiner(
            os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        log2, net2, marking2, fmarking2 = self.obtainPetriNetThroughAlphaMiner(
            os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        log1.sort()
        log1 = log1.sample()
        log1.insert_trace_index_as_event_attribute()
        log2.sort()
        log2.insert_trace_index_as_event_attribute()
        log2 = log2.sample()
        self.assertEqual(log2, log2)
        petri_exporter.export_net(net1, marking1, os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        os.remove(os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        self.assertEqual(len(net1.places), len(net2.places))
        self.assertEqual(len(net1.transitions), len(net2.transitions))
        self.assertEqual(len(net1.arcs), len(net2.arcs))
        final_marking = petri.petrinet.Marking()
        for p in net1.places:
            if not p.out_arcs:
                final_marking[p] = 1
        aligned_traces = token_replay.apply_log(log1, net1, marking1, final_marking)
        self.assertEqual(aligned_traces, aligned_traces)

    def test_applyAlphaMinerToCSV(self):
        # calculate and compare Petri nets obtained on the same log to verify that instances
        # are working correctly
        log1, net1, marking1, fmarking1 = self.obtainPetriNetThroughAlphaMiner(
            os.path.join(INPUT_DATA_DIR, "running-example.csv"))
        log2, net2, marking2, fmarking2 = self.obtainPetriNetThroughAlphaMiner(
            os.path.join(INPUT_DATA_DIR, "running-example.csv"))
        log1.sort()
        log1 = log1.sample()
        log1.insert_trace_index_as_event_attribute()
        log2.sort()
        log2 = log2.sample()
        log2.insert_trace_index_as_event_attribute()
        petri_exporter.export_net(net1, marking1, os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        os.remove(os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        self.assertEqual(len(net1.places), len(net2.places))
        self.assertEqual(len(net1.transitions), len(net2.transitions))
        self.assertEqual(len(net1.arcs), len(net2.arcs))
        final_marking = petri.petrinet.Marking()
        for p in net1.places:
            if not p.out_arcs:
                final_marking[p] = 1
        aligned_traces = token_replay.apply_log(log1, net1, marking1, final_marking)
        self.assertEqual(aligned_traces, aligned_traces)

    def test_alphaMinerVisualizationFromXES(self):
        log, net, marking, fmarking = self.obtainPetriNetThroughAlphaMiner(
            os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        log.sort()
        log = log.sample()
        log.insert_trace_index_as_event_attribute()
        petri_exporter.export_net(net, marking, os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        os.remove(os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        gviz = pn_viz.graphviz_visualization(net)
        self.assertEqual(gviz, gviz)
        final_marking = petri.petrinet.Marking()
        for p in net.places:
            if not p.out_arcs:
                final_marking[p] = 1
        aligned_traces = token_replay.apply_log(log, net, marking, fmarking)
        self.assertEqual(aligned_traces, aligned_traces)

    def test_applyAlphaMinerToProblematicLogs(self):
        logs = os.listdir(PROBLEMATIC_XES_DIR)
        for log in logs:
            try:
                log_full_path = os.path.join(PROBLEMATIC_XES_DIR, log)
                # calculate and compare Petri nets obtained on the same log to verify that instances
                # are working correctly
                log1, net1, marking1, fmarking1 = self.obtainPetriNetThroughAlphaMiner(log_full_path)
                log2, net2, marking2, fmarking2 = self.obtainPetriNetThroughAlphaMiner(log_full_path)
                self.assertEqual(len(net1.places), len(net2.places))
                self.assertEqual(len(net1.transitions), len(net2.transitions))
                self.assertEqual(len(net1.arcs), len(net2.arcs))
                final_marking = petri.petrinet.Marking()
                for p in net1.places:
                    if not p.out_arcs:
                        final_marking[p] = 1
                aligned_traces = token_replay.apply_log(log1, net1, marking1, final_marking)
                self.assertEqual(aligned_traces, aligned_traces)
            except SyntaxError as e:
                logging.info("SyntaxError on log " + str(log) + ": " + str(e))
            except NoConceptNameException as e:
                logging.info("Concept name error on log " + str(log) + ": " + str(e))


if __name__ == "__main__":
    unittest.main()