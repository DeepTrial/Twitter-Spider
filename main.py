from parsing_engine import interface


interface.scrap_main_page(
    account="Mask",
    save_dir="./saver/",
    headless=True,
    page_info="main",
    login=True,
    resume=True
)


# interface.scrap_between_date(
#     account="Mask",
#     start_date="2021-4-1",
#     end_date="2021-4-12",
#     save_dir="./saver/",
#     headless=False
# )
