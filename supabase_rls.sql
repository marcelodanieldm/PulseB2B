-- RLS Policy: Only Pro users can access contact_info and export_csv

-- For leads.contact_info
CREATE POLICY "Pro users can view contact info"
  ON leads
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM profiles WHERE id = auth.uid() AND pro_plan = true
    )
  );

-- For export_csv (replace with your actual table name)
CREATE POLICY "Pro users can export CSV"
  ON export_csv
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM profiles WHERE id = auth.uid() AND pro_plan = true
    )
  );
