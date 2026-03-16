from config import Config
import pandas as pd


class DataProcessor:
    @staticmethod
    def filter_timestamps_for_period(timestamps):
        """Keeps only timestamps that fall within the 2024-2025 range."""
        valid_ts = []
        for ts in timestamps:
            # SMARD chunks usually represent weeks. We include chunks that overlap our range.
            if ts >= (Config.START_MS - 604800000) and ts <= Config.END_MS:
                valid_ts.append(ts)
        return valid_ts

    @staticmethod
    def process_raw_data(raw_rows, column_name):
        """Converts raw JSON rows to a cleaned Pandas DataFrame."""
        if not raw_rows:
            return None
            
        df = pd.DataFrame(raw_rows, columns=['timestamp', column_name])
        
        # Filter strictly to 2024-2025 at the row level
        df = df[(df['timestamp'] >= Config.START_MS) & (df['timestamp'] <= Config.END_MS)]
        
        # Convert timestamp to human-readable datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        # Remove duplicates
        df = df[~df.index.duplicated(keep='first')]
        return df

    @staticmethod
    def merge_datasets(dataframes_dict):
        """Merges all separate dataframes into one master DataFrame."""
        if not dataframes_dict:
            return None

        # Start with the first dataframe to act as the base index
        base_key = list(dataframes_dict.keys())[0]
        df_master = dataframes_dict[base_key]
        
        # Outer join the rest
        for name, df in dataframes_dict.items():
            if name != base_key:
                df_master = df_master.join(df, how='outer')
        
        # Sort chronologically and forward-fill small gaps 
        df_master.sort_index(inplace=True)
        df_master = df_master.ffill() 
        return df_master