import optparse
import os

from flask import Flask, request, jsonify, render_template,Response,send_file
import google_search

app = Flask(__name__, template_folder='../templates')
json_path = 'visualization/data.json'
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    claim = request.form.get('claim_input')
    optparser = optparse.OptionParser()

    optparser.add_option(
        "-i", "--input", default="../input_data/enhanced_claims.txt",
        help="path to the file containing claims"
    )
    optparser.add_option(
        "-o", "--output", default="../output_data/claim",
        help="path_to the output file, each file has a claim and its analysis"
    )
    optparser.add_option(
        "-s", "--stop", default=1,
        help="number of claims to analyze"
    )
    optparser.add_option(
        "-r", "--n_relevant_sent", default=5,
        help="n most releveant sentences in each article."
    )
    optparser.add_option(
        "-t", "--top_search_results", default=10,
        help="limit research to the first r search results retrieved."
    )
    optparser.add_option(
        "-j", "--json_visualization", default='visualization/data.json',
        help="the path to the json output file used by the D3 code to visualize the network."
    )

    opts = optparser.parse_args()[0]
    google_search.main(opts, claim)
    if os.path.isfile(json_path):
        return send_file(json_path, mimetype='application/json')
    else:
        return jsonify({'message': 'Search completed'})

if __name__ == '__main__':
    app.run()
