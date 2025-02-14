from textual.app import App, ComposeResult
from textual.widgets import DataTable, LoadingIndicator, Static, Footer, Header
from textual.containers import Container
from textual import work
from textual.binding import Binding

import json
from node import Node
from time import sleep
import threading


HEADERS = ["Name", "Version", "IP", "Peers", "Synced", "Top", "Verified", "Synced", "Smeshing", "PoST State", "Space Units", "GiB", "Layers"]

class Nodemon(App):

    BINDINGS = [
        Binding("q", "app.quit", "Quit", show=True),
    ]
    CSS_PATH = "nodemon.tcss"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield DataTable(classes='-hidden')
        with Container(id='loading-cont'):
            yield Static('Loading Node Data (this can take a while)', id='loading-message')
            yield LoadingIndicator(id="loading-indicator", name="Loading Node Data")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True

        # Add headers to table
        for index, header in enumerate(HEADERS):
            table.add_column(header, key=str(index))

        # Start worker
        self.update_node_data()


    # This will update the table
    @work(thread=True)
    def update_node_data(self) -> None:

        with open('config.json', 'r') as config_file:
            config = json.load(config_file)

        nodes = []
        for node in config['nodes']:
            node_instance = Node(node)
            nodes.append(node_instance)

        while True:
            table = self.query_one(DataTable)
            threads = []

            # Each node is run as a thread
            for node in nodes:
                thread = threading.Thread(target=node.load_all_data)
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

            # Hide the loading container once data has been loaded
            self.query_one("#loading-cont").add_class("-hidden")
            table.remove_class("-hidden")
            
            # For each node add a row
            for index, node in enumerate(nodes):
                node_data = node.get_node_data()

                if not table.is_valid_row_index(index):
                    table.add_row(node_data['name'], node_data['version'], node_data['host'], node_data['connected_peers'], str(node_data['synced']), str(node_data['top_layer']), str(node_data['verified_layer']), str(node_data['synced_layer']), str(node_data['smeshing']), str(node_data['post_state']), str(node_data['space_units']), str(node_data['size_gib']), str(node_data['assigned_layers_count']), key=str(index))
                else:
                    table.update_cell(str(index), "0", str(node_data['name']))
                    table.update_cell(str(index), "1", str(node_data['version']))
                    table.update_cell(str(index), "2", str(node_data['host']))
                    table.update_cell(str(index), "3", str(node_data['connected_peers']))
                    table.update_cell(str(index), "4", str(node_data['synced']))
                    table.update_cell(str(index), "5", str(node_data['top_layer']))
                    table.update_cell(str(index), "6", str(node_data['verified_layer']))
                    table.update_cell(str(index), "7", str(node_data['synced_layer']))
                    table.update_cell(str(index), "8", str(node_data['smeshing']))
                    table.update_cell(str(index), "9", str(node_data['post_state']))
                    table.update_cell(str(index), "10", str(node_data['space_units']))
                    table.update_cell(str(index), "11", str(node_data['size_gib']))
                    table.update_cell(str(index), "12", str(node_data['assigned_layers_count']))

            sleep(120)

app = Nodemon()
if __name__ == "__main__":
    app.run()