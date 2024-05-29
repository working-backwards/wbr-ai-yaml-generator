import os

import yaml
from openai import OpenAI

METRIC_RETRIEVAL_PROMPT = """
You are an helpful assistant who fetches the metrics from the given csv data of 3-4 row in the string format. 
Follow the below procedure to accomplish this
 - First get the column headers of the csv file
 - Take look at each column values and determine a aggregation factor for the column example -> sum, mean etc and a scaling factor 
 - Generate a csv with 3 columns, as follows
    1) column name: metric
       column values: columns in the csv provided by user 
    2) column name: agg_factor
       column values: aggregation factor of each column in the csv provided by user
    3) column name: scaling_factor
       column values: Values could by either Billion or Million or Thousand or Percent or None

 - You can ignore the `Date` column
 - In the response give only the generated csv and no need of other inference
 - A example of is provided for your reference
 Example -> 
    User csv -> 
    Date,PageViews,PageViews__Target,Defects/Million,MobilePageViews,Desktop Pct,DesktopPageViews,Fatals,Fatals/Million,404s
    "Sun, 05-Jan-2020",56607738,61136357,11980,25109400,0.56,31498338,132,2,678143
    "Mon, 06-Jan-2020",60443381,58630080,11931,27019531,0.55,33423850,152,3,721160
    "Tue, 07-Jan-2020",54667022,58493714,12159,22127770,0.6,32539252,161,3,664716

    Generated csv -> 
    metric,agg_factor,scaling_factor
    PageViews,sum,Million
    PageViews__Target,sum,Million
    Defects/Million,sum,Thousand
    MobilePageViews,sum,Million
    Desktop Pct,mean,Percent
    DesktopPageViews,sum,Million
    Fatals,sum,Million
    Fatals/Million,sum,None
    404s,sum,Thousand

Generate in the following format where you have replace $$your_response with the generated csv
csv_start
$$your_response
csv_end

"""

USER_PROMPT = """
Below is the csv data
{csv_data}
"""

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'], organization=os.environ["ORGANISATION_ID"])


def generate(csv_input: str, temp_file):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            # Set an optional system message. This sets the behavior of the
            # assistant and can be used to provide specific instructions for
            # how it should behave throughout the conversation.
            {
                "role": "system",
                "content": METRIC_RETRIEVAL_PROMPT
            },
            # Set a user message for the assistant to respond to.
            {
                "role": "user",
                "content": USER_PROMPT.format(csv_data=csv_input),
            }
        ],
        temperature=0.4,
        max_tokens=4096
    )

    metric_csv_response = response.choices[0].message.content.strip()

    index_of_start = metric_csv_response.find("csv_start")
    index_of_end = metric_csv_response.rfind("csv_end")

    stripped_response = metric_csv_response[index_of_start + 10:index_of_end]

    lines = stripped_response.split("\n")

    y_scaling_dict = {}
    agg_dict = {}

    for csv_line in lines:
        if len(csv_line) < 1:
            continue
        line_split = csv_line.split(",")
        metric_name = line_split[0]
        if metric_name == "metric":
            continue
        agg_f = line_split[1]
        y_scaling = line_split[2]
        agg_dict[metric_name] = agg_f
        y_scaling_dict[metric_name] = y_scaling

    configs = {}

    wbr_setup_config = {
        'week_ending': 'Please enter a week ending date, <dd-MMM-YYYY> eg: 25-SEP-2021',
        'week_number': 'Enter the week number of week ending date',
        'title': 'A title for your WBR',
        'x_axis_monthly_display': 'trailing_twelve_months'
    }

    configs['setup'] = wbr_setup_config

    metric_config_dict = {}

    for metric, agg in agg_dict.copy().items():
        metric_config_dict[metric] = {'column': metric, 'aggf': agg}

    configs['metrics'] = metric_config_dict

    blocks = []
    scale_dict = {"million": "##MM", "billion": "##BB", "thousand": "##KK", "percent": "##%"}

    for metric, y_scale in y_scaling_dict.copy().items():
        deck_config_dict = {}
        target = None
        if metric + "__Target" in y_scaling_dict:
            target = metric + "__Target"
            y_scaling_dict.__delitem__(metric + "__Target")
        wbr_scale = scale_dict[y_scale.lower()] if y_scale.lower() in scale_dict else None
        block_config = {
            'ui_type': '6_12Graph',
            'title': metric,
            'y_scaling': wbr_scale,
            'metrics': get_metric_block(metric, target)
        }

        deck_config_dict['block'] = block_config
        blocks.append(deck_config_dict)

    configs['deck'] = blocks

    with open(temp_file.name, mode="a") as file:
        yaml.dump(configs, file, sort_keys=False)


def get_metric_block(metric, target):
    metric_block_config = {metric: {'line_style': 'primary', 'graph_prior_year_flag': True}}
    if target is not None:
        metric_block_config[target] = {'line_style': 'target', 'graph_prior_year_flag': False}
    return metric_block_config
