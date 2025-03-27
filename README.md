# README

## What's this?
I was trying to come up with a useful project—something that would help me develop my coding skills while actually being fun to build. But after postponing it for too long due to a lack of exciting ideas, I decided to just start coding... even if it meant making something totally useless.

This is a general-purpose tool that lets you:

- Check your country's currency ISO symbol
- Get current exchange rates  
- Find the currency that matches your height (because why not?)  

Maybe one day, I'll add database support and connect GPT to pull fun facts about the country that matches your best-fit currency. But for now, it's just this.  

## What You Need
- Python 3.11  
- Hope  

## How to Set It Up
1. Make a `.env` file from the template.  
   - For `STOCK_API`, get your own API key from [Currency Freaks](https://currencyfreaks.com/).  
2. Create a virtual environment:  
   ```bash
   python -m venv venv
   ```
3. Activate it
    ```bash
    venv\Scripts\activate
   ```
4. Install packages.
    ```bash
   pip install -r requirements.txt
    ``` 