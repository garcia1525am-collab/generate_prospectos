import time
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import re
import os

class GoogleMapsScraper:
    def __init__(self):
        """Inicializa el scraper"""
        self.driver = None
        self.wait = None
        self.setup_driver()
    
    def setup_driver(self):
        """Configura el navegador Chrome con undetected_chromedriver"""
        options = uc.ChromeOptions()
        
        # Configuraciones estables
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins-discovery")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--no-first-run")
        options.add_argument("--disable-default-apps")
        
        # User-Agent más realista
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            print("✅ Configurando Undetected ChromeDriver...")
            
            # Crear directorio temporal para datos del usuario
            temp_user_data = os.path.join(os.getcwd(), "temp_chrome_profile")
            options.add_argument(f"--user-data-dir={temp_user_data}")
            
            self.driver = uc.Chrome(
                options=options,
                version_main=None,
                driver_executable_path=None,
                use_subprocess=False
            )
            
            self.wait = WebDriverWait(self.driver, 25)
            print("✅ Chrome iniciado correctamente")
            
        except Exception as e:
            print(f"❌ Error configurando Undetected ChromeDriver: {e}")
            print("\n🔄 Intentando configuración alternativa...")
            try:
                options = uc.ChromeOptions()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--headless")
                
                self.driver = uc.Chrome(options=options)
                self.wait = WebDriverWait(self.driver, 25)
                print("✅ Chrome iniciado en modo alternativo")
                
            except Exception as e2:
                print(f"❌ Error en configuración alternativa: {e2}")
                raise

    def scroll_and_load_results(self, max_results=10):
        """Hace scroll inteligente para cargar más resultados de Google Maps"""
        print(f"🔄 Cargando hasta {max_results} resultados...")
        
        # Esperar un momento inicial para que cargue la página
        time.sleep(3)
        
        # Buscar el panel de resultados con selectores más específicos
        results_panel_selectors = [
            "div[role='main']",
            "div.m6QErb.DxyBCb.kA9KIf.dS8AEf",  # Panel lateral de resultados
            "div.Nv2PK.THOPZb",
            "div[data-value='Search results']",
            ".m6QErb",
            "[role='main'] [role='feed']"
        ]
        
        results_panel = None
        for selector in results_panel_selectors:
            try:
                results_panel = self.driver.find_element(By.CSS_SELECTOR, selector)
                if results_panel and results_panel.is_displayed():
                    print(f"✅ Panel de resultados encontrado: {selector}")
                    break
            except:
                continue
        
        unique_urls = set()
        scroll_attempts = 0
        max_scroll_attempts = 20
        no_new_results_count = 0
        
        while len(unique_urls) < max_results and scroll_attempts < max_scroll_attempts:
            scroll_attempts += 1
            
            # Obtener enlaces actuales antes del scroll
            current_links = self.get_current_business_links()
            previous_count = len(unique_urls)
            
            # Agregar nuevos enlaces únicos
            for link in current_links:
                if len(unique_urls) >= max_results:
                    break
                if link and '/maps/place/' in link:
                    unique_urls.add(link)
            
            current_count = len(unique_urls)
            print(f"   📊 Intento {scroll_attempts}: {current_count} resultados únicos encontrados")
            
            # Verificar si encontramos nuevos resultados
            if current_count == previous_count:
                no_new_results_count += 1
            else:
                no_new_results_count = 0
            
            # Si llevamos varios intentos sin nuevos resultados, salir
            if no_new_results_count >= 5:
                print(f"⚠️ No se encontraron nuevos resultados en los últimos {no_new_results_count} intentos")
                break
                
            if current_count >= max_results:
                print(f"✅ ¡Objetivo alcanzado! {current_count} resultados encontrados")
                break
            
            # Estrategias múltiples de scroll
            try:
                if results_panel:
                    # Método 1: Scroll en el panel de resultados (más efectivo)
                    self.driver.execute_script("""
                        arguments[0].scrollBy(0, 800);
                        arguments[0].scrollTop = arguments[0].scrollTop;
                    """, results_panel)
                    
                    # Método 2: Scroll hasta el último elemento visible
                    try:
                        last_result = results_panel.find_elements(By.CSS_SELECTOR, "a[href*='/maps/place/']")
                        if last_result:
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", last_result[-1])
                    except:
                        pass
                        
                else:
                    # Scroll en toda la página si no encontramos el panel
                    self.driver.execute_script("window.scrollBy(0, 1000);")
                
                # Método 3: Usar ActionChains cada ciertos intentos
                if scroll_attempts % 3 == 0:
                    actions = ActionChains(self.driver)
                    actions.send_keys(Keys.PAGE_DOWN).perform()
                    time.sleep(1)
                    actions.send_keys(Keys.END).perform()
                
                # Método 4: Simular scroll con la rueda del mouse
                if scroll_attempts % 4 == 0:
                    try:
                        element_to_scroll = results_panel or self.driver.find_element(By.TAG_NAME, "body")
                        actions = ActionChains(self.driver)
                        actions.move_to_element(element_to_scroll).perform()
                        
                        # Simular múltiples scrolls con rueda
                        for i in range(3):
                            actions.scroll_by_amount(0, 300).perform()
                            time.sleep(0.5)
                    except:
                        pass
                        
            except Exception as e:
                print(f"   ⚠️ Error en scroll {scroll_attempts}: {e}")
            
            # Esperar a que se carguen nuevos resultados
            time.sleep(2.5)
            
            # Intentar hacer clic en "Mostrar más resultados" si existe
            if scroll_attempts % 6 == 0:
                try:
                    # Buscar botones de "Mostrar más" con diferentes métodos
                    load_more_buttons_found = False
                    
                    # Método 1: Selectores CSS directos
                    css_selectors = [
                        "button[jsaction*='load']",
                        ".HlvSq",
                        "button[aria-label*='más']",
                        "button[aria-label*='more']"
                    ]
                    
                    for selector in css_selectors:
                        try:
                            load_more = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if load_more.is_displayed() and load_more.is_enabled():
                                self.driver.execute_script("arguments[0].click();", load_more)
                                print("   🔄 Botón 'Mostrar más' encontrado y clickeado")
                                time.sleep(3)
                                load_more_buttons_found = True
                                break
                        except:
                            continue
                    
                    # Método 2: XPath para texto específico
                    if not load_more_buttons_found:
                        xpath_selectors = [
                            "//*[contains(text(), 'Mostrar más')]",
                            "//*[contains(text(), 'Ver más')]",
                            "//*[contains(text(), 'Show more')]",
                            "//*[contains(text(), 'Load more')]"
                        ]
                        
                        for xpath in xpath_selectors:
                            try:
                                load_more = self.driver.find_element(By.XPATH, xpath)
                                if load_more.is_displayed() and load_more.is_enabled():
                                    self.driver.execute_script("arguments[0].click();", load_more)
                                    print("   🔄 Botón 'Mostrar más' encontrado y clickeado")
                                    time.sleep(3)
                                    break
                            except:
                                continue
                                
                except:
                    pass
        
        print(f"🏁 Scroll completado: {len(unique_urls)} resultados únicos disponibles")
        
        # Si no conseguimos suficientes resultados, intentar una última estrategia
        if len(unique_urls) < max_results and len(unique_urls) > 0:
            print(f"🔍 Intentando estrategia adicional para obtener más resultados...")
            
            # Scroll más agresivo al final
            for i in range(5):
                try:
                    if results_panel:
                        self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", results_panel)
                    else:
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    
                    # Verificar si hay nuevos resultados
                    current_links = self.get_current_business_links()
                    for link in current_links:
                        if len(unique_urls) >= max_results:
                            break
                        if link and '/maps/place/' in link:
                            unique_urls.add(link)
                            
                    if len(unique_urls) >= max_results:
                        break
                        
                except Exception as e:
                    print(f"   ⚠️ Error en scroll final: {e}")
                    break
        
        final_count = len(unique_urls)
        if final_count < max_results:
            print(f"ℹ️ Se obtuvieron {final_count} resultados de {max_results} solicitados")
            print("   Esto puede deberse a que no hay más negocios disponibles en esta búsqueda")
        
        return list(unique_urls)

    def get_current_business_links(self):
        """Obtiene todos los enlaces de negocios visibles actualmente con mejor detección"""
        business_links = []
        
        # Selectores más específicos y completos
        selectors = [
            "a[href*='/maps/place/'][data-value]",  # Más específico
            "a[href*='/maps/place/']",
            "a[data-result-index]",
            ".hfpxzc",
            "a[jsaction*='navigate']",
            "div[role='article'] a[href*='place']",
            ".Nv2PK a[href*='place']",
            "[role='main'] a[href*='/maps/place/']",
            ".THOPZb a[href*='/maps/place/']"
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    try:
                        href = element.get_attribute('href')
                        if href and '/maps/place/' in href and href not in business_links:
                            # Verificar que el elemento sea visible
                            if element.is_displayed():
                                business_links.append(href)
                    except:
                        continue
            except Exception as e:
                continue
        
        # Eliminar duplicados manteniendo el orden
        unique_links = []
        seen = set()
        for link in business_links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)
        
        return unique_links

    def search_businesses(self, url, max_results=10):
        """Busca y extrae información de negocios en Google Maps."""
        print(f"🔍 Accediendo a: {url}")
        
        if "google.com/maps" not in url and "maps.google.com" not in url:
            print("❌ La URL no parece ser una búsqueda válida de Google Maps")
            print("📝 Ejemplo de URL válida: https://www.google.com/maps/search/restaurantes+cerca+de+mi/@19.4326,-99.1332,15z")
            return []
        
        try:
            self.driver.get(url)
            print("⏳ Esperando que cargue la página de resultados...")
            
            # Esperar a que aparezcan los primeros resultados
            time.sleep(5)
            
            # Intentar cerrar cualquier popup o notificación
            try:
                # Posibles botones de cierre o "Aceptar"
                close_buttons = [
                    "button[aria-label*='close']",
                    "button[aria-label*='dismiss']",
                    "button[data-value='Accept']",
                    ".VfPpkd-Bz112c-LgbsSe"  # Botón de Google
                ]
                for selector in close_buttons:
                    try:
                        button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if button.is_displayed():
                            button.click()
                            time.sleep(1)
                            break
                    except:
                        continue
            except:
                pass
            
            # Verificar que hay resultados básicos
            initial_selectors = [
                "a[href*='/maps/place/']",
                "div[role='article']",
                ".Nv2PK"
            ]
            
            found_results = False
            for selector in initial_selectors:
                try:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    found_results = True
                    print(f"✅ Resultados iniciales encontrados con: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not found_results:
                print("❌ No se encontraron resultados iniciales. Verifica la URL de búsqueda.")
                return []
            
            # 🔥 SCROLL AUTOMÁTICO MEJORADO
            unique_urls = self.scroll_and_load_results(max_results)
            
            if not unique_urls:
                print("❌ No se pudieron obtener URLs de negocios.")
                return []
            
            print(f"✅ Se encontraron {len(unique_urls)} negocios únicos para procesar.")
            
            # Limitar a la cantidad solicitada
            urls_to_process = unique_urls[:max_results]
            
            businesses_data = []
            for i, business_url in enumerate(urls_to_process):
                print(f"\n🔍 Procesando negocio {i+1}/{len(urls_to_process)}...")
                data = self.extract_business_data(business_url, i)
                if data:
                    businesses_data.append(data)
                    
                # Pausa entre solicitudes para evitar detección
                time.sleep(2)
            
            return businesses_data
            
        except Exception as e:
            print(f"❌ Error durante la búsqueda: {e}")
            return []

    def extract_business_data(self, url, index):
        """Navega a la página de un negocio y extrae toda su información."""
        business_data = {
            'indice': index, 
            'nombre': 'No disponible', 
            'calificacion': 'No disponible', 
            'num_reviews': 'No disponible', 
            'tipo': 'No disponible', 
            'direccion': 'No disponible', 
            'telefono': 'No disponible', 
            'website': 'No disponible', 
            'email': 'No disponible'
        }
        
        try:
            print(f"   🚗 Navegando a la página del negocio...")
            self.driver.get(url)
            
            # Espera más flexible para diferentes elementos
            selectors_to_wait = [
                "h1.DUwDvf",
                "h1[data-attrid='title']",
                ".x3AX1-LfntMc-header-title-title"
            ]
            
            title_element = None
            for selector in selectors_to_wait:
                try:
                    title_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    break
                except TimeoutException:
                    continue
            
            if not title_element:
                print("   ❌ No se pudo cargar la página del negocio")
                return None
                
            print("   ✅ Página de detalles cargada.")

            # Extracción de datos con múltiples selectores de respaldo
            try:
                name_selectors = ["h1.DUwDvf", "h1[data-attrid='title']", ".x3AX1-LfntMc-header-title-title"]
                for selector in name_selectors:
                    try:
                        business_data['nombre'] = self.driver.find_element(By.CSS_SELECTOR, selector).text
                        break
                    except:
                        continue
            except: 
                pass
                
            try:
                rating_selectors = ["div.F7nice", ".MW4etd", ".ceNzKf"]
                for selector in rating_selectors:
                    try:
                        rating_text = self.driver.find_element(By.CSS_SELECTOR, selector).text
                        parts = rating_text.split('(')
                        if len(parts) > 0: 
                            business_data['calificacion'] = parts[0].strip()
                        if len(parts) > 1: 
                            business_data['num_reviews'] = parts[1].replace(')', '').strip()
                        break
                    except:
                        continue
            except: 
                pass
                
            try:
                type_selectors = ["button.DkEaL", ".YhemCb"]
                for selector in type_selectors:
                    try:
                        business_data['tipo'] = self.driver.find_element(By.CSS_SELECTOR, selector).text
                        break
                    except:
                        continue
            except: 
                pass
                
            try:
                address_selectors = [
                    "button[data-item-id='address']",
                    "[data-item-id='address'] .Io6YTe",
                    ".LrzXr"
                ]
                for selector in address_selectors:
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        address = element.get_attribute('aria-label') or element.text
                        business_data['direccion'] = address.replace('Dirección:', '').strip()
                        break
                    except:
                        continue
            except: 
                pass
                
            try:
                phone_selectors = [
                    "button[data-item-id^='phone:tel:']",
                    "[data-item-id*='phone'] .Io6YTe"
                ]
                for selector in phone_selectors:
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        phone = element.get_attribute('aria-label') or element.text
                        business_data['telefono'] = phone.replace('Teléfono:', '').strip()
                        break
                    except:
                        continue
            except: 
                pass
                
            try:
                website_selectors = [
                    "a[data-item-id='authority']",
                    "a[href^='http']:not([href*='google.com'])"
                ]
                for selector in website_selectors:
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        business_data['website'] = element.get_attribute('href')
                        break
                    except:
                        continue
            except: 
                pass
            
            print(f"   ✅ Extraído: {business_data['nombre']}")
            return business_data

        except TimeoutException:
            print("   ❌ La página del negocio no cargó a tiempo.")
            return None
        except Exception as e:
            print(f"   ⚠️ Error inesperado extrayendo datos: {e}")
            return None

    def save_to_csv(self, businesses, filename='negocios_extraidos.csv'):
        if not businesses:
            print("❌ No hay datos para guardar.")
            return
        
        df = pd.DataFrame(businesses)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n💾 Datos guardados en {filename}")
        print(f"📊 Total de negocios extraídos: {len(businesses)}")
        
        # Mostrar resumen de datos extraídos
        print("\n📋 Resumen de extracción:")
        for col in df.columns:
            no_disponible = (df[col] == 'No disponible').sum()
            disponible = len(df) - no_disponible
            print(f"  {col}: {disponible}/{len(df)} disponibles")
    
    def close(self):
        if self.driver:
            self.driver.quit()
            print("\n🔒 Navegador cerrado")
            
        # Limpiar directorio temporal si existe
        temp_user_data = os.path.join(os.getcwd(), "temp_chrome_profile")
        try:
            if os.path.exists(temp_user_data):
                import shutil
                shutil.rmtree(temp_user_data, ignore_errors=True)
        except:
            pass

def main():
    print("🚀 Google Maps Business Scraper con Scroll Automático Mejorado")
    print("="*70)
    print("💡 Ejemplos de URLs válidas:")
    print("  • https://www.google.com/maps/search/restaurantes+mexicanos+cdmx/@19.4326,-99.1332,13z")
    print("  • https://www.google.com/maps/search/dentistas+cerca+de+mi/@19.4326,-99.1332,15z")
    print("="*70)
    
    scraper = None
    all_businesses = []
    search_count = 0
    
    try:
        scraper = GoogleMapsScraper()
        
        while True:
            search_count += 1
            print(f"\n🔍 BÚSQUEDA #{search_count}")
            print("-" * 30)
            
            # Solicitar URL
            url = input("🌐 Ingresa la URL de búsqueda de Google Maps (o 'salir' para terminar): ").strip()
            
            if url.lower() in ['salir', 'exit', 'quit', 's', '']:
                break
            
            # Validar URL básica
            if "google.com/maps" not in url and "maps.google.com" not in url:
                print("❌ La URL no parece válida. Inténtalo de nuevo.")
                continue
            
            # Pedir número de resultados
            try:
                max_results = int(input(f"📊 ¿Cuántos negocios extraer? (por defecto 10): ") or "10")
                if max_results > 50:
                    print("⚠️ Se recomienda no más de 50 resultados por búsqueda")
                    confirm = input("¿Continuar con más de 50? (s/n): ").strip().lower()
                    if confirm not in ['s', 'si', 'sí']:
                        max_results = 50
            except:
                max_results = 10
            
            # Pedir nombre personalizado para esta búsqueda
            search_name = input(f"🏷️ Nombre para esta búsqueda (ej: 'restaurantes_cdmx'): ").strip()
            if not search_name:
                search_name = f"busqueda_{search_count}"
            
            print(f"\n⚡ Procesando búsqueda: {search_name}")
            print("="*60)
            
            # Realizar búsqueda
            businesses = scraper.search_businesses(url, max_results=max_results)
            
            if businesses:
                # Agregar identificador de búsqueda a cada negocio
                for business in businesses:
                    business['busqueda'] = search_name
                    business['indice_global'] = len(all_businesses) + business['indice']
                
                all_businesses.extend(businesses)
                
                # Guardar esta búsqueda individual
                individual_filename = f'negocios_{search_name}.csv'
                scraper.save_to_csv(businesses, individual_filename)
                
                print(f"✅ Búsqueda '{search_name}' completada: {len(businesses)} negocios")
            else:
                print(f"❌ No se obtuvieron resultados para '{search_name}'")
            
            # Preguntar si continuar
            print(f"\n📈 RESUMEN HASTA AHORA:")
            print(f"   • Búsquedas realizadas: {search_count}")
            print(f"   • Total de negocios: {len(all_businesses)}")
            
            if len(all_businesses) > 0:
                continuar = input(f"\n🔄 ¿Hacer otra búsqueda? (s/n): ").strip().lower()
                if continuar not in ['s', 'si', 'sí', 'y', 'yes']:
                    break
            
        # Guardar archivo consolidado si hay datos
        if all_businesses:
            print(f"\n💾 GUARDANDO ARCHIVO CONSOLIDADO...")
            consolidated_filename = f'todos_los_negocios_consolidado.csv'
            scraper.save_to_csv(all_businesses, consolidated_filename)
            
            # Mostrar resumen final
            print(f"\n📊 RESUMEN FINAL:")
            print(f"   • Total de búsquedas: {search_count}")
            print(f"   • Total de negocios: {len(all_businesses)}")
            print(f"   • Archivo consolidado: {consolidated_filename}")
            
            # Resumen por búsqueda
            from collections import Counter
            busquedas_count = Counter([b['busqueda'] for b in all_businesses])
            print(f"\n📋 NEGOCIOS POR BÚSQUEDA:")
            for busqueda, count in busquedas_count.items():
                print(f"   • {busqueda}: {count} negocios")
                
        else:
            print("\n❌ No se obtuvieron datos en ninguna búsqueda.")
            
    except KeyboardInterrupt:
        print("\nℹ️ Proceso interrumpido por el usuario")
        if all_businesses:
            scraper.save_to_csv(all_businesses, 'negocios_parcial.csv')
            print("💾 Datos parciales guardados en 'negocios_parcial.csv'")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
    
    finally:
        if scraper:
            scraper.close()
        print(f"\n✅ Proceso completado. ¡Hasta luego! 👋")

if __name__ == "__main__":
    main()