if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QMessageBox
    
    def gui_main():
        app = QApplication(sys.argv)
        try:
            V_source, R_transformer, load_resistances = get_user_inputs()
            results = simulate_grid(V_source, R_transformer, load_resistances)
            display_results(results)
            plot_results(results)
            export_to_excel(results)
            QMessageBox.information(None, "Success", "Simulation completed! Check console and plots.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Simulation failed: {str(e)}")
        sys.exit(app.exec_())

    gui_main()