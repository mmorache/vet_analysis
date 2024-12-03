import pandas as pd

class CatDataCleaner:
    def __init__(self, input_file="litter_robot.csv", output_file="cat_weights.csv", year = '2024'):
        self.input_file = input_file
        self.output_file = output_file
        self.year = year
        self.df = None

    def _prep_raw(self):
        self.df = pd.read_csv(self.input_file)
        self.df['Timestamp'] = pd.to_datetime(self.df['Timestamp'] + ', 2024', format='%m/%d %I:%M%p, %Y')
        self.df['Weight'] = self.df['Value'].str.replace(' lbs', '', regex=False).astype(float)
        self.df = self.df.drop(["Activity", "Value"], axis=1)

    def _add_cats(self):
        self.df = self.df[(self.df['Weight'] >= 7.0) & (self.df['Weight'] <= 13.0)]
        self.df['Cat'] = 'undetermined'
        self.df.loc[(self.df['Weight'] >= 12.2) & (self.df['Weight'] <= 12.9), 'Cat'] = 'Gilbert'
        self.df.loc[(self.df['Weight'] >= 11.0) & (self.df['Weight'] <= 12.1), 'Cat'] = 'Frankie'
        self.df.loc[(self.df['Weight'] >= 9.7) & (self.df['Weight'] <= 10.9), 'Cat'] = 'Catness'
        self.df.loc[(self.df['Weight'] >= 7.7) & (self.df['Weight'] <= 8.9), 'Cat'] = 'Speck'

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
        self._consolidate_weights()
        self.df.to_csv(self.output_file, index=False)

# Example usage:
#cleaner = CatDataCleaner()  # Use default file names
#cleaner.process_data()


