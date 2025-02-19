# ParliaMint Topic Detection & Summarization

## Overview

This project is a prototype aimed at exploring topic detection methods and summarization models. The primary goal is to evaluate and experiment with various techniques to enhance the understanding and summarization of parliamentary data.


## Objectives

- **Prototype Development**: Create a foundational prototype for topic detection and summarization.
- **Evaluation**: Assess the effectiveness of different topic detection methods.
- **Experimentation**: Experiment with various summarization models to determine the most effective approaches.

## Features

- **Topic Detection**: Implement and test multiple methods for detecting topics within parliamentary data.
- **Summarization**: Develop and evaluate summarization models to generate concise summaries of the data.

**Important Caveat**: At the moment, the goal of using zero-shot-classification with a given set of political topics failed. For that reason, I used an LDA-approach and labelled the 5 topics arbitrarily. That means the topic distribution shown in the dashboard is not correct at the moment.

## Usage

As this is a prototype, the usage instructions are subject to change based on ongoing evaluations and experiments. Please refer to the project documentation for the latest updates.


## Streamlit App Usage

To interact with the prototype, we have developed a Streamlit application that provides a user-friendly interface for topic detection and summarization.

You can access the deployed version of the Streamlit application through the following link:

[ParliaMint Topic Detection & Summarization Dashboard](https://parliamint.streamlit.app/)

This dashboard provides an interactive interface for exploring topic detection and summarization features on parliamentary data. It includes functionalities for uploading data, applying various topic detection methods, generating summaries, and visualizing the results.

### Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/lutz-he/ParliaMintDetection.git
    cd ParliaMintDetection
    ```

2. **Install the required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Running the App

To start the Streamlit application, run the following command in your terminal:
```bash
streamlit run streamlit_app.py
```

### Using the App

Once the app is running, you can access it in your web browser at `http://localhost:8501`. The app provides the following functionalities:

- **Upload Data**: Upload your parliamentary data in the supported format.
- **Topic Detection**: Select and apply different topic detection methods to your data.
- **Summarization**: Generate summaries of the detected topics using various summarization models.
- **Visualization**: View visual representations of the detected topics and summaries.

For detailed instructions on how to use each feature, please refer to the in-app guidance and tooltips.

### Example

Here is a quick example of how to use the app:

1. **Upload your data**: Click on the "Browse files" button and select your data file.
2. **Select a topic detection method**: Choose a method from the dropdown menu.
3. **Generate summaries**: Click on the "Summarize" button to generate summaries of the detected topics.
4. **View results**: Explore the results through the provided visualizations and summary texts.

Feel free to experiment with different methods and parameters to see how they affect the results.

## Contributing

Contributions are welcome! If you have ideas for improving the topic detection methods or summarization models, please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgements

We would like to thank all contributors and researchers whose work has inspired and supported this project.
