import pandas as pd

class CatDataCleaner:
    def __init__(self, input_files=None, output_file="cat_weights.csv"):
        if input_files is None:
            self.input_files = [
                "litter_robot_1.csv",
                "litter_robot_2.csv",
                "litter_robot_3.csv",
                "litter_robot_4.csv",
                "litter_robot_5.csv",
                "litter_robot_6.csv",
                "litter_robot_7.csv",
                "litter_robot_8.csv",
                "litter_robot_9.csv",
                "litter_robot_10.csv",
                "litter_robot_11.csv"
            ]
        else:
            self.input_files = input_files
        self.output_file = output_file
        self.df = None

    def _get_year(self, month):
        """Determine the year based on the month."""
        if month in [11, 12]:
            return 2024
        return 2025

    def _prep_raw(self):
        dfs = []
        for file in self.input_files:
            df = pd.read_csv(file)
            # Extract month from the timestamp and determine the year
            df['Month'] = pd.to_datetime(df['Timestamp'], format='%m/%d %I:%M%p').dt.month
            df['Year'] = df['Month'].apply(self._get_year)

            # Convert Timestamp with the determined year
            df['Timestamp'] = pd.to_datetime(
                df['Timestamp'] + ', ' + df['Year'].astype(str), format='%m/%d %I:%M%p, %Y'
            )

            df['Weight'] = df['Value'].str.replace(' lbs', '', regex=False).astype(float)
            df = df.drop(["Activity", "Value", "Month", "Year"], axis=1)
            dfs.append(df)

        self.df = pd.concat(dfs)
        # Drop duplicates based on 'Timestamp' and keep the first occurrence
        self.df = self.df.drop_duplicates(subset='Timestamp', keep='first')


    def _add_cats(self):
        self.df = self.df[(self.df['Weight'] >= 7.0) & (self.df['Weight'] <= 13.0)]
        self.df['Cat'] = 'undetermined'
        self.df.loc[(self.df['Weight'] >= 12.2) & (self.df['Weight'] <= 13.0), 'Cat'] = 'Gilbert'
        self.df.loc[(self.df['Weight'] >= 11.0) & (self.df['Weight'] <= 12.1), 'Cat'] = 'Frankie'
        self.df.loc[(self.df['Weight'] >= 9.5) & (self.df['Weight'] <= 10.9), 'Cat'] = 'Catness'
        self.df.loc[(self.df['Weight'] >= 7.5) & (self.df['Weight'] <= 8.9), 'Cat'] = 'Speck'

    def _drop_undetermined(self):
        self.df = self.df[self.df['Cat'] != 'undetermined']

# TODO: this mess needs refactoring
    def _consolidate_weights(self):
        cats = self.df['Cat'].unique()
        cat_dfs = []

        for cat in cats:
            cat_df = self.df[self.df['Cat'] == cat].sort_values('Timestamp').reset_index(drop=True)
            rows_to_drop = []
            i = 0
            while i < len(cat_df) - 1:
                time_diff = (cat_df.loc[i + 1, 'Timestamp'] - cat_df.loc[i, 'Timestamp']).total_seconds() / 60
                if time_diff <= 15:
                    consecutive_rows = [i]
                    j = i + 1
                    while j < len(cat_df):
                        time_diff_next = (cat_df.loc[j, 'Timestamp'] - cat_df.loc[j-1, 'Timestamp']).total_seconds() / 60
                        if time_diff_next <= 15:
                            consecutive_rows.append(j)
                            j += 1
                        else:
                            break
                    avg_weight = cat_df.loc[consecutive_rows, 'Weight'].mean()
                    cat_df.loc[i, 'Weight'] = round(avg_weight, 1)
                    rows_to_drop.extend(consecutive_rows[1:])
                    i = j
                else:
                    i += 1
            cat_df = cat_df.drop(rows_to_drop).reset_index(drop=True)

            if not cat_df.empty:
                cat_dfs.append(cat_df)

        self.df = pd.concat(cat_dfs).sort_values('Timestamp').reset_index(drop=True)


    def process_data(self):
        self._prep_raw()
        self._add_cats()
        self._drop_undetermined() 
        self._consolidate_weights()
        self.df.to_csv(self.output_file, index=False)

# Example usage:
#cleaner = CatDataCleaner()  # Use default file names
#cleaner.process_data()


