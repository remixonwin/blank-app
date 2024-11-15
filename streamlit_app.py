from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
import time
import os
import streamlit as st

# Define the folder to save the screenshot
folder_path = 'screenshots'

def main():
    st.title("Webpage Screenshot Tool")
    
    if 'url' not in st.session_state:
        st.session_state.url = ''
    
    url = st.text_input("Enter the web address:", value=st.session_state.url)
    
    if st.button("Take Screenshot") and url:
        st.session_state.url = url
        st.session_state.screenshot_index = 0
        if 'screenshot_index' not in st.session_state:
            st.session_state.screenshot_index = 0

        if os.path.exists(folder_path):
            screenshots = [f for f in os.listdir(folder_path) if f.endswith('.png')]
            if screenshots:
                col1, _, col3 = st.columns([1, 2, 1])
                with col1:
                    if st.button("Previous") and st.session_state.screenshot_index > 0:
                        st.session_state.screenshot_index -= 1
                with col3:
                    if st.button("Next") and st.session_state.screenshot_index < len(screenshots) - 1:
                        st.session_state.screenshot_index += 1

                current_screenshot = screenshots[st.session_state.screenshot_index]
                img_path = os.path.join(folder_path, current_screenshot)
                st.image(img_path, use_container_width=True)
                st.markdown(f"Screenshot {st.session_state.screenshot_index + 1} of {len(screenshots)}")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.add_argument('--headless')
        firefox_options.add_argument('--no-sandbox')
        firefox_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=firefox_options)
        
        try:
            # Open webpage
            driver.get(url)
            
            # Wait for page to load (up to 10 seconds)
            time.sleep(5)  # Initial wait
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Wait for any dynamic content to load
            driver.execute_script("return document.readyState") == "complete"
            
            total_height = driver.execute_script("return document.body.scrollHeight")
            driver.set_window_size(1920, total_height)
            
            current_height = 0
            screenshot_number = 1
            
            while current_height < total_height:
                # Wait after each scroll
                time.sleep(2)
                file_path = os.path.join(folder_path, f'screenshot_{screenshot_number}.png')
                driver.save_screenshot(file_path)
                
                current_height += driver.get_window_size()['height']
                driver.execute_script(f"window.scrollTo(0, {current_height});")
                screenshot_number += 1
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        finally:
            driver.quit()

if __name__ == "__main__":
    main()
    # Display screenshots in a carousel
    if os.path.exists(folder_path):
        screenshots = [f for f in os.listdir(folder_path) if f.endswith('.png')]
        if screenshots:
            st.write("Screenshots taken:")
            for screenshot in sorted(screenshots):
                img_path = os.path.join(folder_path, screenshot)
                st.image(img_path, use_container_width=True)
                st.markdown("---")

