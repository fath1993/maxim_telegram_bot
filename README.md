# Telegram Bot to Buy Subscriptions and Download from Websites

This project is a Telegram bot that allows users to purchase subscriptions for various websites such as Envato and Motion Array, and provides direct download access for subscribed content. The bot simplifies the process of managing multiple subscriptions and downloading resources via Telegram.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features

- Purchase subscriptions for multiple websites (e.g., Envato, Motion Array).
- Directly download content through the Telegram bot after purchasing a subscription.
- User authentication and account management through Telegram.
- View and manage active subscriptions.
- Receive download links directly in Telegram chat.
- Secure payment process with support for multiple payment gateways.

## Installation

To run this project locally, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/telegram-bot-subscriptions.git
    ```

2. Navigate into the project directory:
    ```bash
    cd telegram-bot-subscriptions
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up your Telegram bot by obtaining an API token from [BotFather](https://core.telegram.org/bots#botfather) and adding it to the `.env` file:
    ```bash
    TELEGRAM_API_KEY=your_telegram_api_key
    ```

5. Configure the API keys for the supported websites (e.g., Envato, Motion Array) in the `.env` file:
    ```bash
    ENVATO_API_KEY=your_envato_api_key
    MOTION_ARRAY_API_KEY=your_motion_array_api_key
    ```

6. Start the bot:
    ```bash
    python bot.py
    ```

## Usage

- **Start the bot**: Open Telegram and search for your bot by name or username.
- **Purchase a subscription**: Follow the bot’s instructions to select a website and purchase a subscription.
- **Download content**: After subscribing, the bot will send you download links for content directly within the chat.

## Contributing

Contributions are welcome! If you’d like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/new-feature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/new-feature`).
5. Open a Pull Request.

## License

This projec
