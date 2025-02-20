# ParliaMint Topic Detection & Summarization

This project is a prototype aimed at exploring topic detection methods and summarization models for the development of a streamlit dashboard. The idea of the dashboard is to 

1. **Topic Detection**:   
Visualize the **prevalence of specific topics** in parliamentary debates over time in order.
    - this can be used for a long-term analysis of parliamentary debates or
    - to identify specific debates relevant to the user
2. **Summarization**:   
For a selected date (e.g. the user has identified a certain day, where a certain topic was debated) the dashboard features a **mini-summary for each debate** that took place on that day.


> **Disclaimer**: This project is a prototype developed within 12 hours and is under active development. The current data base is the 2022 subset of the [ParlaMint parliamentary data of the Netherlands](https://www.clarin.si/repository/xmlui/handle/11356/1910). The current topic detection and generative text summarization models can be seen as placeholder models for demonstrative purposes only. See also the discussion below on further ideas and issues.


## How to use
As this is a prototype, the usage instructions are subject to change based on ongoing evaluations and experiments.

### Online Dashboard


To interact with the prototype, we have developed a Streamlit application that provides a user-friendly interface for topic detection and summarization.

You can access the deployed version of the Streamlit application through the following link:    
[https://parliamint.streamlit.app/](https://parliamint.streamlit.app/)


### Local Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/lutz-he/parlia-mint.git
    cd parlia-mint
    ```

2. **Install the required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

To start the Streamlit application, run the following command in your terminal:
```bash
streamlit run streamlit_app.py
```

Once the app is running, you can access it in your web browser at `http://localhost:8501`.

## Current Issues & Ideas

#### data & models
- Streamline application to other subsets of the data
- Find and make work a zero-shot classifier for topic modelling on candidate topics
- Evaluate and search for alternatives for summarization model

#### streamlit app
- Enable clickable events on the graph to subset date selection for debate summaries
- Fix workaround "sneaky_bars" & "sneaky_points" (failed to dodge bars and points, so I tweaked the x-axis values depending on the grouping variable)
- Work on design
- Work on more intuitive UX


## Contributing

Contributions are welcome! If you have ideas for improving the topic detection methods or summarization models, please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgements

| Component                        | Resource                                                                                   |
|----------------------------------|--------------------------------------------------------------------------------------------|
| Data                             | [ParlaMint parliamentary data of the Netherlands](https://www.clarin.si/repository/xmlui/handle/11356/1910) |
| Topic detection zero-shot classifier | [valhalla/distilbart-mnli-12-3](https://huggingface.co/valhalla/distilbart-mnli-12-3)     |
| Summarization                        | [t5-small](https://huggingface.co/t5-small)                                               |
